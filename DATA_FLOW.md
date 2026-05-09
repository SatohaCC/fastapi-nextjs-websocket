# Chat Data Flow (Function List)

本システムにおけるチャットメッセージの送信から受信、およびロスト復旧までのデータの流れと、関与する主要な関数の一覧です。

## 1. 送信フロー (Frontend → Backend → DB)
ユーザーがメッセージを送信し、PostgreSQL に永続化されるまでのステップ。

| ステップ | レイヤー | ファイルパス | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Frontend (UI) | `features/chat/components/GlobalChat.tsx` | `handleSubmit` | ユーザー入力を取得 |
| 2 | Frontend (API) | `features/websocket/api.ts` | `sendMessage` | バックエンド REST API (POST) へ送信 |
| 3 | Backend (API) | `app/presentation/api/messages.py` | `send_message` | エンドポイント。`Depends(get_uow)` で UoW を取得 |
| 4 | Backend (App) | `app/application/uow.py` | `__aenter__` | **UoW トランザクション開始**。DB セッションを確保 |
| 5 | Backend (App) | `app/application/services/chat_service.py` | `send_message` | ビジネスロジック。下書きエンティティの作成 |
| 6 | Backend (Infra) | `sa_message_repository.py` | `save` | `messages` テーブルに保存。DB 側で ID が採番される |
| 7 | Backend (Domain)| `app/domain/entities/message.py` | `to_payload` | **カプセル化**: エンティティ自身が配信用 Payload を生成 |
| 8 | Backend (Infra) | `sa_outbox_repository.py` | `save` | `delivery_feeds` テーブルに保存 (Outbox) |
| 9 | Backend (App) | `app/application/uow.py` | `commit` | **DB コミット**。メッセージと Outbox を同時に確定 |
| 10 | Backend (App) | `app/application/uow.py` | `__aexit__` | セッションのクローズ |

---

## 2. 中継フロー (DB → RelayWorker → Redis)
DB に保存された Outbox データを検知し、メッセージング層 (Redis) へ中継するステップ。

| ステップ | レイヤー | ファイルパス | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Relay (Worker) | `relay_worker.py` | `_listener_task` | PostgreSQL の `LISTEN` により新着を即座に検知 |
| 2 | Relay (Worker) | `relay_worker.py` | `_relay_loop` | 未配信レコードのポーリングループ |
| 3 | Relay (Infra) | `sa_outbox_repository.py` | `get_pending` | `SKIP LOCKED` を用いて安全にレコードを取得 |
| 4 | Relay (Worker) | `relay_worker.py` | `redis.publish` | Redis の Pub/Sub チャンネルへメッセージを流す |
| 5 | Relay (Infra) | `sa_outbox_repository.py` | `mark_processed` | 配信完了したレコードを `PROCESSED` に更新 |

---

## 3. 受信フロー (Redis → WebSocket → Frontend)
Redis に届いたメッセージを WebSocket を通じてブラウザへ届け、画面に表示するステップ。

| ステップ | レイヤー | ファイルパス | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Backend (Sub) | `redis_subscriber.py`| `redis_subscriber` | Redis を `SUBSCRIBE` して新着を待ち受ける |
| 2 | Backend (App) | `app/domain/services/feed_routing.py` | `route` | ルーティング戦略（全配信/個別）の決定 |
| 3 | Backend (WS) | `presentation/websockets/manager.py` | `broadcast` | 接続中の WebSocket クライアントへ JSON 送信 |
| 4 | Frontend (WS) | `features/websocket/hooks/useWebSocket.ts` | `onMessage` | WebSocket 経由で JSON データを受信 |
| 5 | Frontend (Dist) | `features/websocket/handlers/index.ts` | `dispatchMessage` | 受信イベントを適切なハンドラへ振り分け |
| 6 | Frontend (Handler)| `features/websocket/handlers/chatHandler.ts` | `handleChatMessage` | `setChatMessages` を呼び出しステートを更新 |
| 7 | Frontend (UI) | `features/chat/components/GlobalChat.tsx` | (再描画) | React ステート変更を検知し画面に反映 |

---

## 4. 復旧フロー (ロスト検知時の再同期)
ネットワーク断絶などで WebSocket メッセージを逃した場合のリカバリステップ。

| ステップ | レイヤー | ファイルパス | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Frontend (Sync) | `features/websocket/hooks/useMessageSync.ts` | `fetchMissingFeeds` | ギャップ検知時、不足分の取得をリクエスト |
| 2 | Frontend (API) | `features/websocket/api.ts` | `fetchFeeds` | 履歴取得 API (GET) を呼び出し |
| 3 | Backend (API) | `app/presentation/api/feeds.py` | `get_feeds_after` | 指定した `sequence_id` 以降のフィードを DB 検索 |
| 4 | Frontend (Sync) | `features/websocket/hooks/useMessageSync.ts` | (State Update) | 取得した過去分を既存メッセージにマージ |

---

## 5. WebSocket 接続確立フロー（初期ロード含む）
ユーザーが Workspace を開いた際に WebSocket を確立し、初期履歴をロードするステップ。

| ステップ | レイヤー | ファイルパス | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Frontend (Hook) | `features/websocket/hooks/useConnection.ts` | `connectWs` | `token`, `last_chat_id`, `last_request_id` をクエリパラメータに付与して `new WebSocket` |
| 2 | Backend (WS) | `app/presentation/websockets/endpoint.py` | `websocket_endpoint` | `Depends(get_ws_authenticated_user)` で JWT を検証し `username` を取得 |
| 3 | Backend (WS) | `app/presentation/websockets/manager.py` | `ChatManager.connect` | `websocket.accept()` → `connections` dict に登録 |
| 4a | Backend (WS) | `app/presentation/websockets/endpoint.py` | (初回接続: `last_chat_id` が `None`) | `chat_service.get_recent_messages()` を呼び出し最新50件を取得 |
| 4b | Backend (WS) | `app/presentation/websockets/endpoint.py` | (再接続: `last_chat_id` あり) | `feed_service.get_feeds_after(SequenceName("chat_global"), ...)` でギャップ分を取得 |
| 5 | Backend (WS) | `app/presentation/websockets/endpoint.py` | (for h in history) | `ChatResponse.from_domain(h, is_history=True)` に変換し WebSocket へ逐次送信 |
| 6 | Backend (WS) | `app/presentation/websockets/endpoint.py` | (リクエスト履歴) | `last_request_id` の有無に応じて `request_service` または `feed_service` でリクエスト履歴を送信 |
| 7 | Backend (WS) | `app/presentation/websockets/endpoint.py` | `connection_service.handle_user_join` | 初回接続時のみ JOIN イベントを記録（`last_chat_id` と `last_request_id` が共に `None` の場合） |
| 8 | Frontend (Hook) | `features/websocket/hooks/useConnection.ts` | `socket.onopen` | `setIsConnected(true)`、`resetPingTimeout()` でタイマー開始 |
| 9 | Frontend (Hook) | `features/websocket/hooks/useConnection.ts` | `socket.onmessage` | 受信ごとに `onMessage(event, socket)` を呼び出し |
| 10 | Frontend (Dist) | `features/websocket/handlers/index.ts` | `dispatchMessage` | イベントタイプを判定して適切なハンドラへ振り分け |
| 11 | Frontend (Handler) | `features/websocket/handlers/chatHandler.ts` | `handleChatMessage` | ID 重複チェック付きで `setChatMessages` を呼び出しステートに追加 |

---

## 6. Heartbeat / Ping-Pong フロー（接続維持）
接続が生きているかを定期確認し、無応答なら切断するステップ。

| ステップ | レイヤー | ファイルパス | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Backend (WS) | `app/presentation/websockets/endpoint.py` | `asyncio.create_task(heartbeat(...))` | 接続確立後にハートビートタスクを起動 |
| 2 | Backend (WS) | `app/presentation/websockets/manager.py` | `heartbeat` | `PING_INTERVAL` 秒待機後に `pong_event.clear()` → `{"type": "ping"}` を送信 |
| 3 | Frontend (Handler) | `features/websocket/handlers/systemHandler.ts` | `handlePing` | ping 受信 → `{"type": "pong"}` を即時送信 |
| 4 | Frontend (Hook) | `features/websocket/hooks/useConnection.ts` | `resetPingTimeout` | pong 送信時に `PING_TIMEOUT_MS`（17秒）タイマーをリセット |
| 5 | Backend (WS) | `app/presentation/websockets/endpoint.py` | (メインループ: `PongMessage`) | pong 受信 → `pong_event.set()` |
| 6 | Backend (WS) | `app/presentation/websockets/manager.py` | `asyncio.wait_for(pong_event.wait(), ...)` | `PONG_TIMEOUT` 秒以内に pong が来るか確認 |
| 7a | Backend (WS) | `app/presentation/websockets/manager.py` | (正常) | pong 確認 → ループ継続 |
| 7b | Backend (WS) | `app/presentation/websockets/manager.py` | (タイムアウト) | `websocket.close(code=1001, reason="pong timeout")` → 切断フローへ |

---

## 7. 切断・自動再接続フロー
ネットワーク断絶や Heartbeat タイムアウトで接続が切れた際の自動回復ステップ。

| ステップ | レイヤー | ファイルパス | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | (原因) | — | — | ネットワーク断絶 / Heartbeat タイムアウト / サーバー側 `close()` |
| 2 | Frontend (Hook) | `features/websocket/hooks/useConnection.ts` | `socket.onclose` | `setIsConnected(false)`、`clearPingTimeout()`、手動切断でなければ再接続を予約 |
| 3 | Frontend (Hook) | `features/websocket/hooks/useConnection.ts` | `setTimeout(connectWs, delay)` | **指数バックオフ**（初期1秒、最大30秒）でリトライを遅延実行 |
| 4 | Backend (WS) | `app/presentation/websockets/endpoint.py` | (`WebSocketDisconnect` catch) | `ws_manager.disconnect(websocket, username)` を呼び出し |
| 5 | Backend (WS) | `app/presentation/websockets/manager.py` | `ChatManager.disconnect` | `connections` dict から該当 WebSocket を削除、ユーザーの最後の接続なら key ごと削除 |
| 6 | Backend (App) | `app/application/services/connection_service.py` | `handle_user_leave` | LEAVE SystemEvent を生成し Outbox に保存（→ フロー8へ） |
| 7 | Frontend (Hook) | `features/websocket/hooks/useConnection.ts` | `connectWs` (リトライ) | `last_chat_id` / `last_request_id` を引き継いで再接続（→ フロー5 ステップ1へ） |

---

## 8. システムイベント（入退室）配信フロー
ユーザーの入退室を Outbox 経由で全クライアントへブロードキャストするステップ。

| ステップ | レイヤー | ファイルパス | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Backend (App) | `app/application/services/connection_service.py` | `handle_user_join` / `handle_user_leave` | JOIN / LEAVE の `SystemEvent` エンティティを生成 |
| 2 | Backend (Domain) | `app/domain/entities/system_event.py` | `to_payload` | `SystemEventPayload` を生成（`sequence_name="system_global"`） |
| 3 | Backend (Infra) | `app/infrastructure/persistence/sa_outbox_repository.py` | `save` | `delivery_feeds` テーブルへ保存、`NOTIFY` を発行 |
| 4 | Backend (App) | `app/application/uow.py` | `commit` | DB コミット |
| 5 | — | — | — | → **フロー2（中継フロー）**へ: RelayWorker が検知し Redis へ publish |
| 6 | — | — | — | → **フロー3（受信フロー）**へ: Subscriber が受信し `BroadcastStrategy` で全クライアントへ配信 |
| 7 | Frontend (Handler) | `features/websocket/handlers/systemHandler.ts` | (JOIN / LEAVE ハンドラ) | 入退室イベントを UI に反映 |

---

## 9. Outbox クリーンアップフロー（バックグラウンド）
処理済みの古い Outbox レコードを定期削除するバックグラウンドステップ。

| ステップ | レイヤー | ファイルパス | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Backend (Main) | `app/main.py` | `lifespan` | アプリ起動時に `asyncio.TaskGroup` 内で `cleanup_worker` タスクを起動 |
| 2 | Backend (Infra) | `app/infrastructure/messaging/cleanup_worker.py` | `cleanup_worker` | `interval_seconds`（デフォルト 3600秒 = 1時間）待機後に実行 |
| 3 | Backend (App) | `app/application/uow.py` | `async with uow_factory()` | 毎回新しい UoW（DB セッション）を生成（長時間セッション保持を回避） |
| 4 | Backend (App) | `app/application/services/outbox_management_service.py` | `cleanup_old_feeds(hours=24)` | 24時間以上前に処理済みになったレコードを削除対象として特定 |
| 5 | Backend (Infra) | `app/infrastructure/persistence/sa_outbox_repository.py` | `delete_old_processed_feeds(hours=24)` | `DELETE FROM delivery_feeds WHERE status=PROCESSED AND processed_at < NOW()-24h` |
