# リフレッシュトークン仕様書

## 目標

アクセストークン（15分）とリフレッシュトークン（7日）の2種類を発行し、
BFF が透過的に自動リフレッシュすることで、ユーザーに再ログインを求める頻度を削減する。

## Cookie 設計

```
bff_session  HttpOnly; SameSite=Lax; maxAge=15分  ← AES暗号化済みアクセストークン
bff_refresh  HttpOnly; SameSite=Lax; maxAge=7日   ← AES暗号化済みリフレッシュトークン
```

JS からは両方とも読み取り不可。BFF サーバーだけが復号して使用する。

## 自動リフレッシュフロー

```
BFF ルート（proxy / me / ws-ticket）
    │
    ├─ bff_session を復号 → FastAPI 呼び出し
    │
    ├─ 200: そのままレスポンス返却
    │
    └─ 401:
          │
          ├─ bff_refresh を復号 → POST /api/auth/refresh
          │
          ├─ 成功: 新 bff_session + 新 bff_refresh を Set-Cookie してリトライ
          │
          └─ 失敗: 401 をそのまま返す（フロントがログインページへ）
```

## 実装構成とファイル

### バックエンド (FastAPI)

*   `domain/primitives/primitives.py`: `RefreshToken` ValueObject
*   `infrastructure/config.py`: トークン有効期限の設定 (`ACCESS_TOKEN_EXPIRE_MINUTES=15`, `REFRESH_TOKEN_EXPIRE_DAYS=7`)
*   `application/interfaces/auth.py`: `TokenProvider`（トークン生成・検証インターフェース）
*   `infrastructure/auth/jwt_service.py`: `type` クレーム（"access" / "refresh"）による誤用防止を含む JWT サービス
*   `application/services/auth_service.py`: `login()` および `refresh()` 処理
*   `presentation/api/auth.py`: `POST /api/auth/refresh` エンドポイント

### フロントエンド (Next.js)

*   `lib/server/session.ts`: `tryRefreshSession()` による API 呼び出しと Cookie の再設定処理
*   `app/api/auth/login/route.ts`: ログイン成功時に `bff_session` (15分) と `bff_refresh` (7日) の二重 Cookie を発行
*   `app/api/auth/logout/route.ts`: ログアウト時に両方の Cookie を削除
*   `app/api/proxy/[...path]/route.ts`: BFF プロキシ経由で 401 エラー（アクセストークン期限切れ）時に自動で `tryRefreshSession` を走り込ませて透過的リトライを実行

## JWT クレーム設計

```json
// アクセストークン
{ "sub": "alice", "type": "access", "exp": <15分後> }

// リフレッシュトークン
{ "sub": "alice", "type": "refresh", "exp": <7日後> }
```

`verify_token` は `type != "access"` を拒否、`verify_refresh_token` は `type != "refresh"` を拒否。
リフレッシュトークンをアクセストークンとして使う誤用を防止する。

## Refresh Token Rotation (RTR) と データベース無効化

### 安全性の担保
1.  **一回限りの利用 (RTR)**: `POST /api/auth/refresh` は、アクセストークンの更新時に毎回**新しいリフレッシュトークン**も再発行します。
2.  **データベース永続化とハッシュ管理**: 発行したリフレッシュトークンは、データベースの `refresh_tokens` テーブルにセキュアにハッシュ化して保存します。
3.  **即時無効化 (キルスイッチ)**:
    *   リフレッシュトークンが使用されるたびに、古いトークンはデータベースから物理削除（DELETE）されます。
    *   ユーザーがログアウトした際には、そのセッションのリフレッシュトークンを DB から削除して即座に無効化します。
    *   ユーザー単位で全リフレッシュトークンを一括削除する無効化機構（`delete_by_user_id`）も実装済みで、将来のパスワード変更・アカウント削除機能における強制ログアウトに利用できます。

## 既知の制限とトレードオフ

*   **Cookie maxAge と JWT exp の二重管理**: JWT の有効期限を Cookie より 1 分短く設定することで不整合を防ぎます。
