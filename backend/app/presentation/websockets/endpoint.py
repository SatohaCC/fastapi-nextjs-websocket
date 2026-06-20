"""WebSocket エンドポイントの定義とメッセージハンドリング。"""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Annotated, Any
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import TypeAdapter, ValidationError

from ...application.interfaces.presence import PresenceStore
from ...application.outbox.delivery_feed import (
    SequenceId,
    SequenceName,
    direct_request_sequence,
)
from ...application.services.connection_service import ConnectionService
from ...application.services.direct_request_service import DirectRequestService
from ...application.services.feed_query_service import FeedQueryService
from ...application.services.global_chat_service import GlobalChatService
from ...domain.entities.user import User
from ...domain.exceptions import DomainException
from ...infrastructure.config import settings
from ...infrastructure.rate_limiter import FixedWindowRateLimiter
from ..dependencies import (
    get_chat_manager,
    get_chat_message_rate_limiter,
    get_connection_service,
    get_direct_request_rate_limiter,
    get_direct_request_service,
    get_feed_query_service,
    get_global_chat_service,
    get_presence_store,
    get_status_update_rate_limiter,
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
    PresenceStateServerMessage,
    StopTypingServerMessage,
    TypingClientMessage,
    TypingServerMessage,
    UpdateDirectRequestStatusClientMessage,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websockets"])


def has_recovery_hole(last_id: int, min_retained: int | None, head: int | None) -> bool:
    """クライアントの cursor が Outbox の保持窓より下（= 復旧不能な穴）かを判定します。

    24h クリーンアップで古い feed が削除されると、cursor 直後の区間が Outbox から
    失われる。この場合、Outbox 由来の差分だけでは欠落区間を埋められないため、
    永続テーブルからの補填が必要になる。

    Args:
        last_id: クライアントが保持する cursor（最後に受信した sequence_id）。
        min_retained: Outbox に現存する最小 sequence_id（無ければ None）。
        head: 採番済みの最大 sequence_id（無ければ None）。

    Returns:
        cursor より上に未受信領域があり、かつ cursor 直後が削除済みなら True。
    """
    if head is None or head <= last_id:
        # 新規データが無い（cursor が最新）→ 穴なし。
        return False
    # 全削除済み（min_retained is None）か、最小保持 seq が cursor+1 より上なら、
    # cursor 直後の feed が消えている＝穴あり。
    return min_retained is None or min_retained > last_id + 1


async def _send_initial_data(
    websocket: WebSocket,
    user: User,
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
        # Outbox の保持窓より古い cursor（穴）を検知したら、永続テーブルの recent を
        # is_history で補填する。これらは seq を持たないため cursor は前進しないが、
        # 後続の available feed が head まで cursor を前進させる。クライアントは id で
        # 重複排除するため、補填分と available feed が重なっても問題ない。
        min_retained, head = await feed_service.get_sequence_bounds(sequence_name)
        if has_recovery_hole(last_id, min_retained, head):
            history = await history_fetcher()
            for item in history:
                await websocket.send_json(
                    response_model.from_domain(item, is_history=True).model_dump(
                        mode="json"
                    )
                )

        feeds = await feed_service.get_feeds_after(
            sequence_name, SequenceId(last_id), user.userid
        )
        from .schemas import create_server_message_from_feed

        for feed in feeds:
            resp_dto = create_server_message_from_feed(feed, is_history=True)
            await websocket.send_json(resp_dto.model_dump(mode="json"))


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user: Annotated[User, Depends(get_ws_authenticated_user)],
    global_chat_service: Annotated[GlobalChatService, Depends(get_global_chat_service)],
    direct_request_service: Annotated[
        DirectRequestService, Depends(get_direct_request_service)
    ],
    feed_service: Annotated[FeedQueryService, Depends(get_feed_query_service)],
    connection_service: Annotated[ConnectionService, Depends(get_connection_service)],
    ws_manager: Annotated[ChatManager, Depends(get_chat_manager)],
    presence_store: Annotated[PresenceStore, Depends(get_presence_store)],
    chat_message_rate_limiter: Annotated[
        FixedWindowRateLimiter, Depends(get_chat_message_rate_limiter)
    ],
    direct_request_rate_limiter: Annotated[
        FixedWindowRateLimiter, Depends(get_direct_request_rate_limiter)
    ],
    status_update_rate_limiter: Annotated[
        FixedWindowRateLimiter, Depends(get_status_update_rate_limiter)
    ],
    last_chat_id: Annotated[int | None, Query()] = None,
    last_request_id: Annotated[int | None, Query()] = None,
) -> None:
    """WebSocket メインハンドラ"""
    logger.debug("WebSocket authenticated as: %s", user.username.value)
    # ローカルインスタンスの socket 登録（ブロードキャスト先の管理に必要）。
    # session_id を紐付けることで、特定セッションのみを対象にした強制切断
    # （revoke_session）が他デバイスの接続を巻き込まないようにする。
    session_id = getattr(websocket.state, "session_id", None)
    await ws_manager.connect(user.id, user.username.value, websocket, session_id)
    # 在席判定はクラスタ全体の共有ストアで行う（スケールアウト時に在席が分裂しない）。
    # 接続ごとに一意な ID を払い出し、TTL 付きで登録する。生存中は定期的に
    # refresh して期限を延長し、クラッシュ時は TTL 経過で自動失効させる。
    conn_id = uuid4().hex
    became_online = await presence_store.add_connection(user.username.value, conn_id)

    # add_connection 済みのため、init 失敗の早期 return を含む全終了経路で必ず
    # remove_connection するよう、外側の try/finally で在席カウントを管理する。
    try:
        try:
            await _send_initial_data(
                websocket=websocket,
                user=user,
                last_id=last_chat_id,
                sequence_name=SequenceName("global_chat"),
                feed_service=feed_service,
                history_fetcher=global_chat_service.get_recent_messages,
                response_model=GlobalChatServerMessage,
            )

            await _send_initial_data(
                websocket=websocket,
                user=user,
                last_id=last_request_id,
                sequence_name=direct_request_sequence(user.userid.value),
                feed_service=feed_service,
                history_fetcher=lambda: direct_request_service.get_tasks_for_user(
                    user.id
                ),
                response_model=DirectRequestServerMessage,
            )

            # 在席はクラスタ全体の接続数の遷移で判断する。再接続（復旧カーソル付き）
            # でも、そのユーザーがクラスタ全体で初接続なら JOIN を配信し、退室
            # （finally の LEAVE）との対称性を保つ。
            if became_online:
                await connection_service.handle_user_join(user.username)

            # 接続したクライアントに現在の在席ロスター（全インスタンス分）を
            # スナップショットとして送る。以降は join/leave 差分で更新され、再接続の
            # たびに再同期されるため、差分の取りこぼしは自己回復する。
            await websocket.send_json(
                PresenceStateServerMessage(
                    usernames=await presence_store.online_usernames()
                ).model_dump(mode="json")
            )

        except WebSocketDisconnect as e:
            logger.info(
                "disconnect during init: user=%s code=%s reason=%r",
                user.username.value,
                e.code,
                e.reason,
            )
            ws_manager.disconnect(websocket, user.id)
            return
        except Exception:
            logger.exception(
                "WebSocket initialization failed for %s", user.username.value
            )
            ws_manager.disconnect(websocket, user.id)
            try:
                await websocket.close(code=1011, reason="Initialization failed")
            except Exception:
                pass
            return

        pong_event = asyncio.Event()
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(heartbeat(websocket, pong_event))
                tg.create_task(
                    _refresh_presence(presence_store, user.username.value, conn_id)
                )
                tg.create_task(
                    _client_message_loop(
                        websocket=websocket,
                        user=user,
                        pong_event=pong_event,
                        global_chat_service=global_chat_service,
                        direct_request_service=direct_request_service,
                        ws_manager=ws_manager,
                        chat_message_rate_limiter=chat_message_rate_limiter,
                        direct_request_rate_limiter=direct_request_rate_limiter,
                        status_update_rate_limiter=status_update_rate_limiter,
                    )
                )
        except* WebSocketDisconnect as eg:
            raise eg.exceptions[0]
        finally:
            ws_manager.disconnect(websocket, user.id)
    finally:
        # 在席カウントを減算し、クラスタ全体で最後の接続が切れたときだけ LEAVE を配信。
        # 別タブ・別インスタンスに接続が残っていれば退室扱いにしない。
        became_offline = await presence_store.remove_connection(
            user.username.value, conn_id
        )
        if became_offline:
            await connection_service.handle_user_leave(user.username)


async def _refresh_presence(
    presence_store: PresenceStore, username: str, conn_id: str
) -> None:
    """生存中の接続として、在席エントリの有効期限を定期的に延長し続ける。

    ``settings.PING_INTERVAL`` 間隔で refresh する。TTL はこの間隔より十分長い
    ため、数回の取りこぼしがあっても期限切れにはならない。TaskGroup が接続終了
    時にこのタスクをキャンセルするので、退室後に在席が復活することはない。
    """
    while True:
        await asyncio.sleep(settings.PING_INTERVAL)
        await presence_store.refresh_connection(username, conn_id)


async def _client_message_loop(
    *,
    websocket: WebSocket,
    user: User,
    pong_event: asyncio.Event,
    global_chat_service: GlobalChatService,
    direct_request_service: DirectRequestService,
    ws_manager: ChatManager,
    chat_message_rate_limiter: FixedWindowRateLimiter,
    direct_request_rate_limiter: FixedWindowRateLimiter,
    status_update_rate_limiter: FixedWindowRateLimiter,
) -> None:
    """クライアントからの inbound メッセージをディスパッチする。"""
    typing_tasks: dict[str, asyncio.Task[None]] = {}

    async def _auto_stop_typing(username: str) -> None:
        """3秒後に stop_typing をブロードキャストしてタスクを削除する。"""
        await asyncio.sleep(3)
        await ws_manager.broadcast(StopTypingServerMessage(username=username))
        typing_tasks.pop(username, None)

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
                    if await chat_message_rate_limiter.is_limited(str(user.id.value)):
                        await websocket.send_json(
                            ErrorServerMessage(
                                text="メッセージの送信頻度が高すぎます。しばらく待ってから再試行してください。"
                            ).model_dump(mode="json")
                        )
                        continue
                    await global_chat_service.send_message(
                        user_id=user.id,
                        username=user.username,
                        text=msg.to_domain(),
                    )
                elif isinstance(msg, DirectRequestClientMessage):
                    if await direct_request_rate_limiter.is_limited(str(user.id.value)):
                        await websocket.send_json(
                            ErrorServerMessage(
                                text="リクエストの送信頻度が高すぎます。しばらく待ってから再試行してください。"
                            ).model_dump(mode="json")
                        )
                        continue
                    recipient_id, text = msg.to_domain()
                    await direct_request_service.send_request(
                        sender_id=user.id,
                        sender=user.username,
                        recipient_id=recipient_id,
                        text=text,
                    )
                elif isinstance(msg, UpdateDirectRequestStatusClientMessage):
                    if await status_update_rate_limiter.is_limited(str(user.id.value)):
                        await websocket.send_json(
                            ErrorServerMessage(
                                text="ステータス更新の頻度が高すぎます。しばらく待ってから再試行してください。"
                            ).model_dump(mode="json")
                        )
                        continue
                    task_id, new_status = msg.to_domain()
                    await direct_request_service.update_status(
                        task_id=task_id,
                        new_status=new_status,
                        operator_id=user.id,
                    )
                elif isinstance(msg, TypingClientMessage):
                    username = user.username.value
                    existing = typing_tasks.get(username)
                    if existing:
                        existing.cancel()
                    await ws_manager.broadcast(TypingServerMessage(username=username))
                    typing_tasks[username] = asyncio.create_task(
                        _auto_stop_typing(username)
                    )
            except DomainException as e:
                await websocket.send_json(
                    ErrorServerMessage(text=str(e)).model_dump(mode="json")
                )
    except RuntimeError:
        pass
    finally:
        for task in typing_tasks.values():
            task.cancel()
    raise WebSocketDisconnect(code=1000, reason="Client loop finished")
