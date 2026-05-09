"""WebSocket エンドポイントの定義とメッセージハンドリング。"""

import asyncio
import json
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import TypeAdapter, ValidationError

from ...application.services.chat_service import ChatService
from ...application.services.connection_service import ConnectionService
from ...application.services.feed_query_service import FeedQueryService
from ...application.services.request_service import RequestService
from ...domain.exceptions import DomainException
from ...domain.primitives.feed import SequenceId, SequenceName
from ...domain.primitives.primitives import Username
from ..dependencies import (
    get_chat_manager,
    get_chat_service,
    get_connection_service,
    get_feed_query_service,
    get_request_service,
    get_ws_authenticated_user,
)
from .manager import ChatManager, heartbeat
from .schemas import (
    ChatMessage,
    ChatResponse,
    ErrorResponse,
    PongMessage,
    RequestMessage,
    RequestResponse,
    StatusUpdateMessage,
    WebSocketMessage,
)

router = APIRouter(tags=["websockets"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    username: Annotated[Username, Depends(get_ws_authenticated_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    request_service: Annotated[RequestService, Depends(get_request_service)],
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
        if last_chat_id is None:
            history = await chat_service.get_recent_messages()
            for h in history:
                await websocket.send_json(
                    ChatResponse.from_domain(h, is_history=True).model_dump(mode="json")
                )
        else:
            chat_feeds = await feed_service.get_feeds_after(
                SequenceName("chat_global"), SequenceId(last_chat_id), username
            )
            for feed in chat_feeds:
                payload = {
                    **feed.payload.to_dict(),
                    "seq": feed.sequence_id.value if feed.sequence_id else None,
                    "sequence_name": feed.sequence_name.value,
                    "is_history": True,
                }
                await websocket.send_json(payload)

        if last_request_id is None:
            req_history = await request_service.get_requests_for_user(username)
            for r in req_history:
                await websocket.send_json(
                    RequestResponse.from_domain(r, is_history=True).model_dump(
                        mode="json"
                    )
                )
        else:
            request_feeds = await feed_service.get_feeds_after(
                SequenceName("requests_global"), SequenceId(last_request_id), username
            )
            for feed in request_feeds:
                payload = {
                    **feed.payload.to_dict(),
                    "seq": feed.sequence_id.value if feed.sequence_id else None,
                    "sequence_name": feed.sequence_name.value,
                    "is_history": True,
                }
                await websocket.send_json(payload)

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

    try:
        while True:
            try:
                data = await websocket.receive_json()
                msg: WebSocketMessage = TypeAdapter(WebSocketMessage).validate_python(
                    data
                )
            except (json.JSONDecodeError, ValidationError) as e:
                await websocket.send_json(
                    ErrorResponse(text=str(e)).model_dump(mode="json")
                )
                continue

            try:
                if isinstance(msg, PongMessage):
                    pong_event.set()
                elif isinstance(msg, ChatMessage):
                    await chat_service.send_message(
                        username=username, text=msg.to_domain()
                    )
                elif isinstance(msg, RequestMessage):
                    recipient, text = msg.to_domain()
                    await request_service.send_request(
                        sender=username,
                        recipient=recipient,
                        text=text,
                    )
                elif isinstance(msg, StatusUpdateMessage):
                    request_id, new_status = msg.to_domain()
                    await request_service.update_status(
                        request_id=request_id,
                        new_status=new_status,
                        operator=username,
                    )
            except DomainException as e:
                await websocket.send_json(
                    ErrorResponse(text=str(e)).model_dump(mode="json")
                )

    except (WebSocketDisconnect, RuntimeError):
        ws_manager.disconnect(websocket, username)
        await connection_service.handle_user_leave(username)
    finally:
        task.cancel()
