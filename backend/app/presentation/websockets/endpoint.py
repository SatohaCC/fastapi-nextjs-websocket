"""WebSocket エンドポイントの定義とメッセージハンドリング。"""

import asyncio
from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import TypeAdapter, ValidationError

from ...application.outbox.delivery_feed import SequenceId, SequenceName
from ...application.services.connection_service import ConnectionService
from ...application.services.direct_request_service import DirectRequestService
from ...application.services.feed_query_service import FeedQueryService
from ...application.services.global_chat_service import GlobalChatService
from ...domain.exceptions import DomainException
from ...domain.primitives.primitives import Username
from ..dependencies import (
    get_chat_manager,
    get_connection_service,
    get_direct_request_service,
    get_feed_query_service,
    get_global_chat_service,
    get_ws_authenticated_user,
)
from .manager import ChatManager, heartbeat
from .schemas import (
    BaseServerMessage,
    ClientMessage,
    DirectRequestClientMessage,
    DirectRequestServerMessage,
    ErrorServerMessage,
    GlobalChatClientMessage,
    GlobalChatServerMessage,
    PongClientMessage,
    UpdateDirectRequestStatusClientMessage,
)

router = APIRouter(tags=["websockets"])


async def _send_initial_data(
    websocket: WebSocket,
    username: Username,
    last_id: int | None,
    sequence_name: SequenceName,
    feed_service: FeedQueryService,
    history_fetcher: Callable[[], Coroutine[Any, Any, list[Any]]],
    response_model: type[BaseServerMessage],
) -> None:
    """履歴またはギャップデータをクライアントに送信します。"""
    if last_id is None:
        history = await history_fetcher()
        for item in history:
            await websocket.send_json(
                response_model.from_domain(item, is_history=True).model_dump(
                    mode="json"
                )
            )
    else:
        feeds = await feed_service.get_feeds_after(
            sequence_name, SequenceId(last_id), username
        )
        from .schemas import create_server_message_from_feed

        for feed in feeds:
            resp_dto = create_server_message_from_feed(feed, is_history=True)
            await websocket.send_json(resp_dto.model_dump(mode="json"))


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    username: Annotated[Username, Depends(get_ws_authenticated_user)],
    global_chat_service: Annotated[GlobalChatService, Depends(get_global_chat_service)],
    direct_request_service: Annotated[
        DirectRequestService, Depends(get_direct_request_service)
    ],
    feed_service: Annotated[FeedQueryService, Depends(get_feed_query_service)],
    connection_service: Annotated[ConnectionService, Depends(get_connection_service)],
    ws_manager: Annotated[ChatManager, Depends(get_chat_manager)],
    last_chat_id: Annotated[int | None, Query()] = None,
    last_request_id: Annotated[int | None, Query()] = None,
) -> None:
    """WebSocket メインハンドラ"""
    print(f"DEBUG: WebSocket authenticated as: {username.value}")
    await ws_manager.connect(username, websocket)

    try:
        # 履歴とギャップの送信
        await _send_initial_data(
            websocket=websocket,
            username=username,
            last_id=last_chat_id,
            sequence_name=SequenceName("global_chat"),
            feed_service=feed_service,
            history_fetcher=global_chat_service.get_recent_messages,
            response_model=GlobalChatServerMessage,
        )

        await _send_initial_data(
            websocket=websocket,
            username=username,
            last_id=last_request_id,
            sequence_name=SequenceName("direct_request"),
            feed_service=feed_service,
            history_fetcher=lambda: direct_request_service.get_tasks_for_user(username),
            response_model=DirectRequestServerMessage,
        )

        if last_chat_id is None and last_request_id is None:
            # 入室イベントの記録
            await connection_service.handle_user_join(username)

    except WebSocketDisconnect:
        # 初期化中の切断はよくあることなので、静かに終了する
        ws_manager.disconnect(websocket, username)
        return
    except Exception as e:
        print(f"[error] WebSocket initialization failed for {username.value}: {e}")
        import traceback

        traceback.print_exc()
        ws_manager.disconnect(websocket, username)
        try:
            await websocket.close(code=1011)  # Internal Error
        except Exception:
            pass
        return

    pong_event = asyncio.Event()
    task = asyncio.create_task(heartbeat(websocket, pong_event))

    # iter_json() は WebSocketDisconnect を内部で吸収するので、
    # 正常切断時はループが普通に終了する。RuntimeError は state 違反の保険。
    try:
        async for data in websocket.iter_json():
            try:
                msg: ClientMessage = TypeAdapter(ClientMessage).validate_python(data)
            except ValidationError as e:
                await websocket.send_json(
                    ErrorServerMessage(text=str(e)).model_dump(mode="json")
                )
                continue

            try:
                if isinstance(msg, PongClientMessage):
                    pong_event.set()
                elif isinstance(msg, GlobalChatClientMessage):
                    await global_chat_service.send_message(
                        username=username, text=msg.to_domain()
                    )
                elif isinstance(msg, DirectRequestClientMessage):
                    recipient, text = msg.to_domain()
                    await direct_request_service.send_request(
                        sender=username,
                        recipient=recipient,
                        text=text,
                    )
                elif isinstance(msg, UpdateDirectRequestStatusClientMessage):
                    task_id, new_status = msg.to_domain()
                    await direct_request_service.update_status(
                        task_id=task_id,
                        new_status=new_status,
                        operator=username,
                    )
            except DomainException as e:
                await websocket.send_json(
                    ErrorServerMessage(text=str(e)).model_dump(mode="json")
                )
    except RuntimeError:
        pass
    finally:
        task.cancel()
        ws_manager.disconnect(websocket, username)
        await connection_service.handle_user_leave(username)
