# リフレッシュトークン実装計画

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

## 実装ステップ

### Phase 1: バックエンド基盤

| # | ファイル | 変更内容 |
|---|---------|---------|
| 1 | `domain/primitives/primitives.py` | `RefreshToken` ValueObject を追加 |
| 2 | `infrastructure/config.py` | `ACCESS_TOKEN_EXPIRE_MINUTES=15`、`REFRESH_TOKEN_EXPIRE_DAYS=7` を追加 |
| 3 | `application/interfaces/auth.py` | `TokenProvider.create_token` の戻り値を `tuple[AuthToken, RefreshToken]` に変更、`verify_refresh_token` を追加 |

### Phase 2: バックエンド実装

| # | ファイル | 変更内容 |
|---|---------|---------|
| 4 | `infrastructure/auth/jwt_service.py` | `create_token` でトークンペアを返す、`type` クレームで誤用防止、`verify_refresh_token` 追加 |
| 5 | `application/services/auth_service.py` | `login` 戻り値変更、`refresh()` 追加 |
| 6 | `presentation/api/auth.py` | `LoginResponse` に `refresh_token` フィールド追加、`POST /api/auth/refresh` エンドポイント追加 |

### Phase 3: フロントエンド

| # | ファイル | 変更内容 |
|---|---------|---------|
| 7 | `lib/server/session.ts` | `tryRefreshSession` 追加（bff_refresh を使って FastAPI /refresh を呼び、新トークンペアを返す） |
| 8 | `app/api/auth/login/route.ts` | `bff_refresh` Cookie をセット、`bff_session` の maxAge を 15 分に変更 |
| 9 | `app/api/auth/logout/route.ts` | `bff_refresh` Cookie も削除 |
| 10 | `app/api/proxy/[...path]/route.ts` | 401 時に `tryRefreshSession` → リトライ |
| 11 | `app/api/auth/me/route.ts` | 同上 |
| 12 | `app/api/auth/ws-ticket/route.ts` | 同上 |

### Phase 4: テスト

| # | 対象 | 内容 |
|---|------|------|
| 13 | `tests/msw/handlers.ts` | ログインレスポンスに `refresh_token` 追加、`POST /api/auth/refresh` ハンドラ追加 |

## JWT クレーム設計

```json
// アクセストークン
{ "sub": "alice", "type": "access", "exp": <15分後> }

// リフレッシュトークン
{ "sub": "alice", "type": "refresh", "exp": <7日後> }
```

`verify_token` は `type != "access"` を拒否、`verify_refresh_token` は `type != "refresh"` を拒否。
リフレッシュトークンをアクセストークンとして使う誤用を防止する。

## Refresh Token Rotation

`POST /api/auth/refresh` は毎回**新しいリフレッシュトークン**も発行する。
BFF は `bff_refresh` Cookie を毎回更新するため、盗まれたリフレッシュトークンの再利用を検知できる。

## 既知のトレードオフ

- **ステートレス**: リフレッシュトークンをサーバー側 DB で管理しないため、即時無効化はできない。
  7 日以内に悪用された場合、有効期限が切れるまで止められない。
- **Cookie maxAge と JWT exp の二重管理**: JWT の有効期限を Cookie より 1 分短く設定することで不整合を防ぐ。
