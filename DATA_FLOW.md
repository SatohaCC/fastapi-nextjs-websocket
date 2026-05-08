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
