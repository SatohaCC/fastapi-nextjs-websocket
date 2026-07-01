---
type: Feature Design Specification
title: 認証・認可 (Authentication & Authorization)
description: BFF認証、JWTセッション、ワンタイムチケット、RTRリフレッシュ、セッション無効化、レートリミット等の設計と実装。
tags: [auth, security, bff, session, ticket]
timestamp: 2026-06-20T23:30:00Z
---

# 認証・認可 (Authentication & Authorization)

本ドキュメントは、システムにおけるユーザー認証、セッション管理、セキュリティ対策、および WebSocket 接続の確立に関する設計と実装仕様をまとめたものです。

---

## 1. オニオンアーキテクチャの各レイヤーにおける実装

### 🔑 ドメイン層 (Domain Layer)
ビジネス概念、識別子、および基本制約の定義。
- [user.py (User エンティティ)](/backend/app/domain/entities/user.py)
  - `userid` (ログインID/ハンドル、一意、不変) と `username` (表示名、非一意、可変) の定義。
- [primitives.py (値オブジェクト)](/backend/app/domain/primitives/primitives.py)
  - `Userid`, `Username`, `Password`, `SessionId`, `TokenHash` などの制約バリデーション。

### 🔑 アプリケーション層 (Application Layer)
ユースケース処理フローと、リポジトリ抽象インターフェース。
- [auth_service.py (認証サービス)](/backend/app/application/services/auth_service.py)
  - ユーザー新規登録（重複チェック、UUIDv7生成）、ログイン（ハッシュ検証、JWT発行）、トークンリフレッシュ（RTR）。
- [auth_management_service.py (セッション管理)](/backend/app/application/services/auth_management_service.py)
  - アクティブセッション（リフレッシュトークンハッシュ）の一覧取得および強制ログアウト処理。
- [user_repository.py (UserRepository)](/backend/app/domain/repositories/user_repository.py)
  - ユーザー永続化の抽象プロトコル。

### 🔑 インフラストラクチャ層 (Infrastructure Layer)
データ永続化と外部サービスの具体的な技術実装。
- [sa_user_repository.py (SQLAlchemy)](/backend/app/infrastructure/persistence/sa_user_repository.py)
  - `users` テーブルに対するデータベースアクセス実装。
- [jwt_service.py (JWT実装)](/backend/app/infrastructure/auth/jwt_service.py)
  - PyJWT による HS256 トークンのエンコード/デコード処理。
- [redis_ticket_store.py (Redis)](/backend/app/infrastructure/auth/redis_ticket_store.py)
  - WebSocket用のワンタイムチケットの Redis での管理（TTL 10秒、GETDEL による使い捨て保証）。

### 🔑 プレゼンテーション層 (Presentation Layer)
APIエンドポイント、BFF、および DTO 変換。
- [auth.py (FastAPI ルーター)](/backend/app/presentation/api/auth.py)
  - `/token`, `/logout`, `/refresh`, `/me`, `/users` 等のエンドポイント。Pydantic DTO を介した入出力。
- [api.ts (BFF/API定義)](/frontend/src/features/auth/api.ts)
  - BFF `/api/auth/login` 等のクライアントAPI定義。
- [useAuth.ts (セッション管理フック)](/frontend/src/features/auth/hooks/useAuth.ts)
  - セッションストレージとの同期、およびログイン状態の保持。
- [useAccountSettings.ts (設定用フック)](/frontend/src/features/auth/hooks/useAccountSettings.ts)
  - アカウントの表示名（`username`）変更処理。

---

## 2. 認証・認可データフロー

### 2.1 ログインフロー (BFF暗号化Cookieパターン)
ブラウザの JavaScript に JWT を露出させないため、BFF（Next.js）で JWT を暗号化（AES-256-GCM）し、`HttpOnly` Cookie に格納します。

```mermaid
sequenceDiagram
    autonumber
    actor Browser as ブラウザ
    participant BFF as BFF (Next.js)
    participant API as バックエンド (FastAPI)
    database DB as PostgreSQL

    Browser->>BFF: POST /api/auth/login\n{userid, password} (CSRFヘッダー付与)
    BFF->>API: POST /api/auth/token\n{username, password}
    Note over API: bcryptによるハッシュ照合<br/>session_id (UUID v7) 生成
    API->>DB: RefreshToken レコード保存 (SHA-256ハッシュ)
    API-->>BFF: JWTペア返却 {access_token, refresh_token}
    Note over BFF: BFF_SECRET でトークンを個別暗号化 (AES-256-GCM)
    BFF-->>Browser: 暗号化Cookieを設定してレスポンス<br/>- bff_session (14分)<br/>- bff_refresh (7日)
```

### 2.2 WebSocket 接続確立 (ワンタイムチケット方式)
ブラウザの WebSocket API はカスタムヘッダーを送信できないため、10秒有効かつ使い捨て（GETDEL）のチケットを仲介します。

```mermaid
sequenceDiagram
    autonumber
    actor Browser as ブラウザ
    participant BFF as BFF (Next.js)
    participant API as バックエンド (FastAPI)
    database Redis as Redis

    Browser->>BFF: GET /api/auth/ws-ticket
    BFF->>API: POST /api/auth/ws-ticket\nAuthorization: Bearer <JWT>
    API->>Redis: SET ws_ticket_<hash> <user_id> EX 10
    API-->>BFF: { ticket: "ws_ticket_..." }
    BFF-->>Browser: { ticket: "ws_ticket_..." }
    Browser->>API: WebSocket接続 (ws://.../ws?ticket=ws_ticket_...)
    API->>Redis: GETDEL ws_ticket_...
    Redis-->>API: ユーザーID (取得と同時に削除)
    alt チケット有効
        API-->>Browser: 101 Switching Protocols (接続確立)
    else チケット無効 / 期限切れ
        API-->>Browser: 1008 Policy Violation (切断)
    end
```

---

## 3. 主要なセキュリティルールと制限

1.  **パスワードハッシュ**: `bcrypt` (ストレッチング回数: `12`) を使用してハッシュ化し、管理画面（SQLAdmin）からも直接閲覧・変更できないように防護。
2.  **CSRF 対策**: 状態変更系（POST等）リクエストに対し、`X-Requested-With` カスタムヘッダーの存在を Next.js Middleware で強制検証。
3.  **レートリミット**: Redis カウンターを用いて、ログイン制限（IPアドレス別: 10回/60秒、ユーザー名別: 20回/15分）を適用。
4.  **セッション強制無効化 (キルスイッチ)**: セッション削除時、Redis Pub/Sub (`session_control` チャンネル) 経由でバックエンドの WebSocket 接続を即座にクローズコード `1008` で強制切断。
    *   個別セッション削除（`DELETE /api/auth/sessions/{id}`）は `session_id` を伴うイベントとして発火され、`ChatManager.force_disconnect_session` により**当該セッションの接続のみ**が切断される（他デバイス・他セッションの接続には影響しない）。`session_id` はワンタイムチケット（`/api/auth/ws-ticket`）の発行時にアクセストークンから取り出され、WebSocket 接続確立時に紐付けられる。
    *   パスワード変更・アカウント削除・パスワードリセットは全セッション無効化が正しい挙動のため、`session_id` を伴わないイベント（`force_disconnect_user`）でそのユーザーの全接続を切断する。
5.  **REST APIアクセストークンのステートレス検証（既知の制限）**: `get_authenticated_user` はアクセストークンの署名・有効期限のみを検証するステートレス設計であり、DB上のセッション有効性（`is_session_valid`）は照会しない。そのため `DELETE /api/auth/sessions/{id}` によるセッション削除は、WebSocket接続（ワンタイムチケット発行時の `is_session_valid` チェック、および `session_control` チャンネル経由の強制切断）には即座に反映されるが、**REST APIのアクセストークンには反映されず、最大 `ACCESS_TOKEN_EXPIRE_MINUTES`（15分）は使用可能なまま残る**。これはJWTアクセストークンのステートレス性（DB照会不要で高速に検証できる利点）を優先した意図的な設計判断であり、既知の受容リスクである。即時失効が必要な操作（パスワード変更・アカウント削除等）は上記の通り全セッションの強制切断で別途対応している。
