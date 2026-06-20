---
type: Feature Design Specification
title: ダイレクトリクエスト (Direct Requests)
description: ユーザー間でのタスク依頼・ステータス更新、Transactional Outbox、ファンアウト配信、およびギャップ検知と再同期の設計。
tags: [direct-requests, tasks, reliability, outbox, websocket]
timestamp: 2026-06-20T16:21:00Z
---

# ダイレクトリクエスト (Direct Requests)

本ドキュメントは、ユーザー間でのタスク依頼の送受信、処理ステータスの更新、信頼性の高い非同期配信（Outboxパターン）、およびネットワーク切断時の整合性確保（ギャップ検知）に関する設計と実装仕様をまとめたものです。

---

## 1. オニオンアーキテクチャの各レイヤーにおける実装

### 📩 ドメイン層 (Domain Layer)
ビジネスモデル、列挙型、およびビジネスルールの定義。
- [task.py (Task エンティティ)](/backend/app/domain/entities/task.py)
  - `Task` エンティティおよび `TaskStatus` 列挙型 (`REQUESTED` -> `PROCESSING` -> `COMPLETED`) の定義。
  - 「自分自身へのリクエストは禁止」「ステータス更新は受信者のみ可能」といったビジネスルールのカプセル化。

### 📩 アプリケーション層 (Application Layer)
ユースケースと、配信ルーティング戦略、およびリポジトリインターフェース。
- [direct_request_service.py (サービス)](/backend/app/application/services/direct_request_service.py)
  - リクエスト新規作成およびステータス更新のユースケース処理。
- [routing_strategies.py (ルーティング戦略)](/backend/app/application/services/routing_strategies.py)
  - `DirectStrategy` による、送信者と受信者それぞれのタイムラインシーケンス（`direct_request:{user_id}`）へのファンアウト制御の定義。
- [task_repository.py (TaskRepository)](/backend/app/domain/repositories/task_repository.py)
  - タスク永続化の抽象プロトコル。

### 📩 インフラストラクチャ層 (Infrastructure Layer)
データベース、トランザクション、およびバックグラウンド配信処理。
- [sa_task_repository.py (SQLAlchemy)](/backend/app/infrastructure/persistence/sa_task_repository.py)
  - `tasks` テーブルへのクエリ処理実装。
- [sa_outbox_repository.py (Outbox)](/backend/app/infrastructure/persistence/sa_outbox_repository.py)
  - メッセージやタスクイベントを確実に配信するためのアウトボックステーブル (`delivery_feeds`) へのアクセス処理。
- [sa_uow.py (Unit of Work)](/backend/app/infrastructure/persistence/sa_uow.py)
  - タスクの保存とアウトボックスへのイベント書き込みを「単一のデータベーストランザクション」としてアトミックにコミットする保証。
- [relay_worker.py (Relay Worker)](/backend/app/infrastructure/messaging/relay_worker.py)
  - PostgreSQL の `LISTEN/NOTIFY` 経由で新規追加されたフィードを非同期に検知し、Redis Pub/Sub チャンネルへ高速パブリッシュするバックグラウンドワーカー。

### 📩 プレゼンテーション層 (Presentation Layer)
エンドポイント、WebSocket、およびフロントエンド UI と状態フック。
- [direct_requests.py (REST API)](/backend/app/presentation/api/direct_requests.py)
  - `GET /api/direct_requests`（履歴取得）および `PATCH /api/direct_requests/{id}/status`（ステータス更新）エンドポイント。
- [endpoint.py (WebSocketルーター)](/backend/app/presentation/websockets/endpoint.py)
  - WebSocket 経由でのダイレクトリクエスト送信の受信と、リアルタイムなステータス変更イベントの配信。
- [DirectRequestPanel.tsx (UI)](/frontend/src/features/direct_request/components/DirectRequestPanel.tsx)
  - ユーザーを選択してタスクを送信するUI、およびリクエスト一覧の表示。
- [useDirectRequestForm.ts (状態管理フック)](/frontend/src/features/direct_request/hooks/useDirectRequestForm.ts)
  - 送信やステータス変更時の**楽観的UIアップデート（Optimistic UI）**およびロールバック制御。

---

## 2. データの流れと配信保証（Transactional Outbox）

ダイレクトリクエストが作成され、それが確実に送信者と受信者の両方にリアルタイムで届くまでのフロー。

```mermaid
sequenceDiagram
    autonumber
    actor Alice as 送信者 (Alice)
    participant BFF as BFF (Next.js)
    participant API as バックエンド (FastAPI)
    database DB as PostgreSQL
    participant Relay as Relay Worker
    database Redis as Redis
    actor Bob as 受信者 (Bob)

    Alice->>BFF: WebSocket / REST経由でタスク送信
    BFF->>API: POST /api/direct_requests (またはWS)
    Note over API: Unit of Work 開始
    API->>DB: 1. tasks テーブルにタスクを INSERT
    API->>DB: 2. delivery_feeds テーブルにイベントを INSERT<br/>(Alice宛て、Bob宛ての2通に展開)
    Note over API: トランザクションコミット & NOTIFY 発行
    API-->>Alice: 送信完了レスポンス (楽観的UIが確定)

    Note over Relay: PostgreSQLのNOTIFYを検知
    Relay->>Redis: Redis Pub/Sub チャネルへパブリッシュ
    Note over API: Redisのチャネルを購読中 (ChatManager)
    API->>Bob: WebSocket接続を通じてリアルタイムにイベント配信
```

---

## 3. 信頼性設計 (Reliability & Resiliency)

### 3.1 厳密なシーケンス連番 (Strict Sequencing)
- 各配信シーケンス（`direct_request:{user_id}`）ごとに、PostgreSQL ネイティブの SEQUENCE オブジェクト（`nextval()`）で連番（`sequence_id`）を発行します。`nextval()` は呼び出し元トランザクションがロールバックしても値が戻らない非トランザクショナルな採番のため、行ロックによる直列化を発生させずに高頻度書き込みへスケールできます（代償として、ロールバック時に稀な欠番が発生し得ますが、クライアント側のギャップ検知ロジックは大小比較のみのため実害はありません）。

### 3.2 ギャップ検知と再同期 (Gap Detection & Catch-up)
- **クライアント側 (Web)**: 受信したイベントの `sequence_id` に飛び（ギャップ）があった場合、一時的に同期中フラグを立て、バックエンドに対して不足しているID範囲を要求（`GET /api/proxy/feeds/direct_requests?after_request_id={last_id}`）して不足分を補填します。
- **再接続時リプレイ**: ネットワークが瞬断して再接続した際、クライアントは保持している最後の `last_request_id` を WebSocket の接続パラメータとして送り、オフライン中に発生した差分イベントを一度に受信します。

### 3.3 レートリミット (Rate Limits)
- **リクエスト送信**: 60秒間に10回まで (`rate_limit:direct_req:{user_id}`)。
- **ステータス更新**: 60秒間に30回まで (`rate_limit:status_update:{user_id}`)。
