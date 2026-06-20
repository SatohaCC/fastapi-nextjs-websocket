---
type: Feature Design Specification
title: グローバルチャット (Global Chat)
description: 全ユーザー向けのリアルタイムチャット配信、メンション補完UI、レートリミット、およびメッセージ永続化の設計。
tags: [global-chat, messages, outbox, websocket, mention]
timestamp: 2026-06-20T16:22:00Z
---

# グローバルチャット (Global Chat)

本ドキュメントは、全ユーザーが参加するパブリックチャットメッセージの送受信、リアルタイムブロードキャスト配信、@メンションによるユーザー名補完UI、およびメッセージの永続化と欠損防止設計についてまとめたものです。

---

## 1. オニオンアーキテクチャの各レイヤーにおける実装

### 💬 ドメイン層 (Domain Layer)
ビジネスモデル、エンティティ、およびバリデーション制約。
- [message.py (Message エンティティ)](/backend/app/domain/entities/message.py)
  - `Message` エンティティの定義。
  - 「メッセージ本文は空文字禁止」「最大2000文字まで」といったビジネスルールのカプセル化。

### 💬 アプリケーション層 (Application Layer)
ユースケースと、配信ルーティング戦略、およびリポジトリインターフェース。
- [global_chat_service.py (ユースケース)](/backend/app/application/services/global_chat_service.py)
  - メッセージの送信処理、および過去ログ取得（ページネーション）のコントロールフロー。
- [routing_strategies.py (ルーティング戦略)](/backend/app/application/services/routing_strategies.py)
  - `GlobalChatStrategy` による、システム共通の単一配信シーケンス（`global_chat`）へのルーティング定義。
- [message_repository.py (MessageRepository)](/backend/app/domain/repositories/message_repository.py)
  - メッセージ永続化の抽象プロトコル。

### 💬 インフラストラクチャ層 (Infrastructure Layer)
データベースアクセス、Redis 購読、および配信制御。
- [sa_message_repository.py (SQLAlchemy)](/backend/app/infrastructure/persistence/sa_message_repository.py)
  - `messages` テーブルに対するクエリ処理実装（before_id/after_id による過去ログのスクロール取得等）。
- [redis_subscriber.py (Redis Subscriber)](/backend/app/infrastructure/messaging/redis_subscriber.py)
  - Redis Pub/Sub チャンネルから流れてくるチャットイベントを検知し、バックエンドの `ChatManager` に引き渡して接続中の全ユーザーへブロードキャストする購読処理。

### 💬 プレゼンテーション層 (Presentation Layer)
エンドポイント、WebSocket、およびフロントエンド UI と状態管理。
- [global_chat.py (REST API)](/backend/app/presentation/api/global_chat.py)
  - `GET /api/global_chat/messages` エンドポイント定義。
- [endpoint.py (WebSocketルーター)](/backend/app/presentation/websockets/endpoint.py)
  - WebSocket 経由でのメッセージ送信（`global_chat` 型メッセージ）の受け入れと、接続中の全クライアントへのブロードキャスト配信。
- [GlobalChatContainer.tsx (UIコンテナ)](/frontend/src/features/global_chat/components/GlobalChatContainer.tsx)
  - チャットタイムライン表示、テキスト入力、@入力によるユーザーメンションドロップダウン UI の補完制御。

---

## 2. メッセージ送信とリアルタイム配信フロー

メッセージが確実に保存され、他の全アクティブユーザーへ即座にブロードキャストされるまでの流れ。

```mermaid
sequenceDiagram
    autonumber
    actor Alice as 送信者 (Alice)
    participant BFF as BFF (Next.js)
    participant API as バックエンド (FastAPI)
    database DB as PostgreSQL
    participant Relay as Relay Worker
    database Redis as Redis
    participant Sub as Redis Subscriber
    actor Bob as 受信者 (Bob)

    Alice->>BFF: WebSocket経由でチャット送信
    BFF->>API: WSメッセージ (type: "global_chat")
    Note over API: Unit of Work 開始
    API->>DB: 1. messages テーブルに保存
    API->>DB: 2. delivery_feeds テーブルに保存 (sequence: "global_chat")
    Note over API: トランザクションコミット & NOTIFY
    API-->>Alice: 送信完了応答

    Note over Relay: NOTIFYを受信
    Relay->>Redis: Redis Pub/Sub チャネルに publish
    Redis->>Sub: Pub/Sub メッセージを受信
    Sub->>Bob: WebSocketを通じてリアルタイムブロードキャスト配信
```

---

## 3. 主要なセキュリティ・信頼性設計

1.  **Transactional Outbox による At-Least-Once 配信**:
    - チャットメッセージを保存する `messages` テーブルへの書き込みと、配信フィードを保存する `delivery_feeds` テーブルへの書き込みを単一トランザクションで行うことで、データベースへの保存とリアルタイム配信の不一致を防ぎます。
2.  **レートリミット**:
    - 過剰な連続投稿によるサーバー負荷およびチャット荒らしを防ぐため、Redis を用いたレートリミット（10回 / 10秒）をユーザーごとに課しています（キー: `rate_limit:chat_msg:{user_id}`）。
3.  **クライアント側スクロール同期**:
    - 新しいチャットメッセージを受信した際、スクロール位置が最下部付近にある場合のみ自動スクロールし、ユーザーが過去ログを読んでいる際にスクロールが強制的に飛ばされないように制御しています。
