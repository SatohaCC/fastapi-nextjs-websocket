# BFF + チケット方式認証 — 設計資料

## 1. なぜこの設計が必要か

### 旧設計の問題点

```
ブラウザ
├── localStorage / sessionStorage に JWT を保存
└── fetch("/api/...", { headers: { Authorization: "Bearer <JWT>" } })
```

- **XSS 脆弱性**: スクリプトインジェクションが1件でも成功すれば `sessionStorage.getItem("token")` で JWT を盗み取れる
- **トークン漏洩 = セッション乗っ取り**: JWT は有効期限まで無効化できないため、盗まれると取り消しが難しい

### 新設計の目標

> **ブラウザ上で動く JavaScript コードに JWT を一切見せない。**

---

## 2. アーキテクチャ全体像

```
┌─────────────────────────────────────────────────────┐
│  Browser (Client Side)                              │
│                                                     │
│  ┌────────────────┐     Cookie (HttpOnly)           │
│  │  React / Next  │◄────────────────────────────┐  │
│  │  (JS実行環境)  │     bff_session=<暗号化済み> │  │
│  └───────┬────────┘                             │  │
│          │ HTTP/WS (Cookieは自動付与)            │  │
└──────────┼──────────────────────────────────────┼──┘
           │                                      │
           ▼                                      │
┌──────────────────────────────┐                  │
│  BFF (Next.js API Routes)    │                  │
│  ─ サーバーサイドのみで動作 ─ │──────────────────┘
│                              │
│  /api/auth/login   ────────► Cookie をセット (Set-Cookie)
│  /api/auth/logout  ────────► Cookie を削除
│  /api/auth/me      ────────► Cookie → 復号 → FastAPI /me
│  /api/auth/ws-ticket ──────► Cookie → 復号 → FastAPI チケット発行
│  /api/proxy/[...path] ─────► Cookie → 復号 → FastAPI 各エンドポイント
│                              │
└──────────────┬───────────────┘
               │ Authorization: Bearer <JWT>  ← ここだけでJWTが流れる
               ▼
┌──────────────────────────────┐
│  FastAPI (Backend)           │
│                              │
│  POST /api/auth/token  (認証)│
│  GET  /api/auth/me           │
│  POST /api/auth/ws-ticket    │
│  WebSocket /ws?ticket=<...>  │
└──────────────────────────────┘
               │
               ▼
           Redis (チケット一時保管)
```

---

## 3. ログインフロー

```
Browser                    BFF (Next.js)              FastAPI          Redis
   │                            │                        │               │
   │  POST /api/auth/login      │                        │               │
   │  {username, password}      │                        │               │
   │ ─────────────────────────► │                        │               │
   │                            │  POST /api/auth/token  │               │
   │                            │  {username, password}  │               │
   │                            │ ──────────────────────► │               │
   │                            │  200 {access_token: <JWT>}             │
   │                            │ ◄────────────────────── │               │
   │                            │                        │               │
   │                            │ AES-256-GCM で JWT を暗号化            │
   │                            │ → bff_session=<IV:暗号文:AuthTag>      │
   │                            │                        │               │
   │  200 {username: "alice"}   │                        │               │
   │  Set-Cookie: bff_session=<暗号化済み>                │               │
   │    HttpOnly; Secure; SameSite=Lax                   │               │
   │ ◄───────────────────────── │                        │               │
   │                            │                        │               │
   │  ※ JS は JWT を参照不可   │                        │               │
```

**ポイント:**
- BFF はレスポンスに `{username}` だけを返す（JWT は返さない）
- `HttpOnly` Cookie のためブラウザの JS から読み取り不可
- Cookie の値は暗号化済みなので、Cookie が漏れても即座に JWT は取り出せない

---

## 4. REST API プロキシフロー

```
Browser                    BFF /api/proxy/[...path]    FastAPI
   │                            │                        │
   │  POST /api/proxy/global_chat/messages              │
   │  (Cookie: bff_session=<暗号化済み> が自動付与)     │
   │ ─────────────────────────► │                        │
   │                            │ Cookie を読み取り      │
   │                            │ AES-256-GCM 復号       │
   │                            │ → JWT 取得             │
   │                            │                        │
   │                            │  POST /api/global_chat/messages
   │                            │  Authorization: Bearer <JWT>
   │                            │ ──────────────────────► │
   │                            │  200 OK                │
   │                            │ ◄────────────────────── │
   │  200 OK                    │                        │
   │ ◄───────────────────────── │                        │
```

---

## 5. WebSocket 接続フロー（チケット方式）

WebSocket は `HttpOnly` Cookie を `ws://` 接続時のハンドシェイクに直接使えない（`WebSocket` コンストラクタはカスタムヘッダーを設定できない）という制約があります。そのため**ワンタイムチケット**を経由します。

```
Browser            BFF /api/auth/ws-ticket   FastAPI         Redis
   │                        │                   │               │
   │  GET /api/auth/ws-ticket                   │               │
   │  (Cookie: bff_session が自動付与)          │               │
   │ ──────────────────────► │                  │               │
   │                         │ Cookie 復号 → JWT取得            │
   │                         │  POST /api/auth/ws-ticket       │
   │                         │  Authorization: Bearer <JWT>    │
   │                         │ ─────────────────► │            │
   │                         │                   │  SET ws_ticket_<random>
   │                         │                   │  = "alice"  │
   │                         │                   │  EX 10 (秒) │
   │                         │                   │ ────────────► │
   │                         │  200 {ticket: "ws_ticket_<random>"}
   │                         │ ◄───────────────── │            │
   │  200 {ticket: "ws_ticket_<random>"}         │            │
   │ ◄──────────────────────  │                  │               │
   │                          │                  │               │
   │  WebSocket ws://fastapi/ws?ticket=ws_ticket_<random>       │
   │ ──────────────────────────────────────────► │              │
   │                                             │  GETDEL ws_ticket_<random>
   │                                             │ ─────────────────────────►│
   │                                             │  "alice"      │
   │                                             │ ◄─────────────────────────│
   │                                             │ チケット検証OK・削除済み  │
   │  WebSocket 接続確立                         │               │
   │ ◄──────────────────────────────────────────  │              │
```

**チケットの特性:**
| 項目 | 内容 |
|------|------|
| 生成 | `secrets.token_urlsafe(32)` — 256bit の暗号論的乱数 |
| 有効期限 | 10秒（Redis TTL） |
| 使い捨て | `GETDEL` で取得と同時に削除（再利用不可） |
| Redis キー形式 | `ws_ticket_<base64url>` |

---

## 6. 実装ファイルマップ

### フロントエンド (Next.js)

```
frontend/src/
├── app/api/auth/
│   ├── login/route.ts        # POST: FastAPI認証 → Cookie発行
│   ├── logout/route.ts       # POST: Cookie削除
│   ├── me/route.ts           # GET:  Cookie復号 → FastAPI /me プロキシ
│   └── ws-ticket/route.ts    # GET:  Cookie復号 → FastAPI チケット発行
│
├── app/api/proxy/
│   └── [...path]/route.ts    # GET/POST/PUT/PATCH/DELETE: 汎用プロキシ
│
├── lib/server/
│   └── session.ts            # AES-256-GCM 暗号化・復号ユーティリティ
│                             # 'server-only' インポートでクライアントへの混入を防止
│
└── features/common/websocket/hooks/
    └── useConnection.ts      # WebSocket接続前にチケットをフェッチ
```

### バックエンド (FastAPI)

```
backend/app/
├── application/interfaces/
│   └── auth.py               # TicketStore プロトコル定義
│
├── infrastructure/auth/
│   └── redis_ticket_store.py # Redis ベースのチケットストア実装
│
└── presentation/
    ├── api/auth.py            # POST /api/auth/ws-ticket エンドポイント
    └── dependencies.py        # get_ticket_store(), get_ws_authenticated_user()
```

---

## 7. 暗号化仕様

### アルゴリズム: AES-256-GCM

```
平文 (JWT)
    │
    ▼
┌─────────────────────────────────────────┐
│  暗号化 (encryptSession)                │
│                                         │
│  key = SHA256(BFF_SECRET) → 32バイト    │
│  iv  = crypto.randomBytes(12)           │
│  cipher = AES-256-GCM(key, iv)          │
│  encrypted = cipher.update(JWT) + final │
│  authTag = cipher.getAuthTag()          │
└─────────────────────────────────────────┘
    │
    ▼
Cookie値: "<ivHex>:<encryptedHex>:<authTagHex>"
```

**GCM モードを選んだ理由:**
- **認証付き暗号 (AEAD)**: `authTag` により改ざん検知が可能（CBC モードにはない）
- Cookie の値が攻撃者によって書き換えられた場合、復号時にエラーとなり `null` を返す

---

## 8. 脅威モデルと対策まとめ

| 脅威 | 旧設計 | 新設計 |
|------|--------|--------|
| XSS による JWT 窃取 | **危険**: `sessionStorage` は JS から読み取り可能 | **防御**: `HttpOnly` Cookie は JS から読み取り不可 |
| Cookie値の漏洩（通信ログ・サーバーログ・物理アクセス等） | - | **軽減 (多層防御)**: `HttpOnly` で JS からは読み取り不可。さらに値が何らかの手段で漏れても、AES-256-GCM 暗号化済みなので平文 JWT は取り出せない |
| WebSocket URL での JWT 露出 | **危険**: `?token=<JWT>` がブラウザ履歴・ログに残る | **防御**: `?ticket=<乱数>` は10秒で失効・使い捨て |
| チケットの再利用 | - | **防御**: `GETDEL` で取得と同時に削除 |
| CSRF | `SameSite=Lax` で通常のクロスサイトPOSTはブロック | 同左（変化なし） |
| チケット総当たり | - | **防御**: 256bit 乱数 × 10秒 TTL で事実上不可能 |

---

## 9. 既知の制限と今後の改善案

### 現状の制限

1. **`BFF_SECRET` のフォールバック**: 環境変数未設定時はデフォルト値を使用。本番環境では例外を投げるべき。

   ```typescript
   // 推奨改善
   if (!process.env.BFF_SECRET && process.env.NODE_ENV === "production") {
     throw new Error("BFF_SECRET must be set in production");
   }
   ```

2. **プロキシのパス検証なし**: `/api/proxy/[...path]` は FastAPI の全エンドポイントへの転送が可能。許可パスのホワイトリスト化が望ましい。

3. **Cookie の有効期限と JWT の有効期限が独立**: Cookie の `maxAge` が切れても Redis のセッションは別管理のため、同期ロジックが複雑になりうる。

### 改善案

- **リフレッシュトークン対応**: 現在は `access_token` のみ保管。`refresh_token` を別 Cookie に保管することで長期セッションを安全に実現できる。
- **セッションの明示的無効化**: Redis にセッションIDをキーとして保管し、ログアウト時に削除することで、Cookie が漏れても即座に無効化できる。
