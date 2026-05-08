# Chat Data Flow (Function List)

本システムにおけるチャットメッセージの送信から受信、およびロスト復旧までのデータの流れと、関与する主要な関数の一覧です。

## 1. 送信フロー (Frontend → Backend → DB)
ユーザーがメッセージを送信し、PostgreSQL に永続化されるまでのステップ。

| ステップ | レイヤー | ファイル | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Frontend (UI) | `GlobalChat.tsx` | `handleSubmit` | ユーザー入力を取得 |
| 2 | Frontend (API) | `api/messages.ts` | `postMessage` | バックエンド REST API (POST) へ送信 |
| 3 | Backend (API) | `api/messages.py` | `send_message` | FastAPI エンドポイント。DTO のバリデーション |
| 4 | Backend (App) | `chat_service.py` | `send_message` | **中心ロジック**。UoW トランザクションを開始 |
| 5 | Backend (Domain)| `message.py` | `to_payload` | エンティティを配信用データ構造へ変換 |
| 6 | Backend (Infra) | `sa_message_repo.py`| `save` | `messages` テーブルにレコードを保存 |
| 7 | Backend (Infra) | `sa_outbox_repo.py` | `save` | `delivery_feeds` テーブルに保存 (Outbox) |
| 8 | Backend (App) | `uow.py` | `commit` | DB コミット (ここでメッセージと Outbox が確定) |

---

## 2. 中継フロー (DB → RelayWorker → Redis)
DB に保存された Outbox データを検知し、メッセージング層 (Redis) へ中継するステップ。

| ステップ | レイヤー | ファイル | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Relay (Worker) | `relay_worker.py` | `_listener_task` | PostgreSQL の `LISTEN` により新着を即座に検知 |
| 2 | Relay (Worker) | `relay_worker.py` | `_relay_loop` | 未配信レコードのポーリングループ |
| 3 | Relay (Infra) | `sa_outbox_repo.py` | `get_pending` | `SKIP LOCKED` を用いて安全にレコードを取得 |
| 4 | Relay (Worker) | `relay_worker.py` | `redis.publish` | Redis の Pub/Sub チャンネルへメッセージを流す |
| 5 | Relay (Infra) | `sa_outbox_repo.py` | `mark_processed` | 配信完了したレコードを `PROCESSED` に更新 |

---

## 3. 受信フロー (Redis → WebSocket → Frontend)
Redis に届いたメッセージを WebSocket を通じてブラウザへ届け、画面に表示するステップ。

| ステップ | レイヤー | ファイル | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Backend (Sub) | `redis_subscriber.py`| `redis_subscriber` | Redis を `SUBSCRIBE` して新着を待ち受ける |
| 2 | Backend (App) | `feed_routing.py` | `route` | ルーティング戦略（全配信/個別）の決定 |
| 3 | Backend (WS) | `manager.py` | `broadcast` | 接続中の WebSocket クライアントへ JSON 送信 |
| 4 | Frontend (WS) | `useWebSocket.ts` | `onMessage` | WebSocket 経由で JSON データを受信 |
| 5 | Frontend (Sync) | `useMessageSync.ts` | `handleIncoming` | **ギャップ検知**: `sequence_id` の連続性を確認 |
| 6 | Frontend (UI) | `GlobalChat.tsx` | `setMessages` | React ステートを更新し、画面に再描画 |

---

## 4. 復旧フロー (ロスト検知時の再同期)
ネットワーク断絶などで WebSocket メッセージを逃した場合のリカバリステップ。

| ステップ | レイヤー | ファイル | 関数/メソッド | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Frontend (Sync) | `useMessageSync.ts` | `syncMissing` | ギャップ検知時、不足分の取得をリクエスト |
| 2 | Frontend (API) | `api/feeds.ts` | `getFeedsAfter` | 履歴取得 API (GET) を呼び出し |
| 3 | Backend (API) | `api/feeds.py` | `get_feeds_after` | 指定した `sequence_id` 以降のフィードを DB 検索 |
| 4 | Frontend (Sync) | `useMessageSync.ts` | `mergeMessages` | 取得した過去分を現在のリストにマージ |
