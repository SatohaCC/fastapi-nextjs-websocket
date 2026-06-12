# WebSocket Chat — Outbox + LISTEN/NOTIFY + DDD

- 学習用リポジトリ：WebSocket のロスト対策と、PostgreSQL を核とした高信頼・低負荷なメッセージング設計を学ぶために作成。
- 細かい学習過程はこっち  [my-1st-WebSocket-fastapi](https://github.com/SatohaCC/my-1st-WebSocket-fastapi)

## 1. 機能一覧
本システムは、リアルタイム性が求められる以下の機能を備えています。
- **グローバルチャット**: 全参加者によるリアルタイムな情報共有。
- **ダイレクトリクエスト**: 特定ユーザー間での依頼・承認ワークフロー。
    - ステータス管理（未着手, 進行中, 完了）が可能。
- **自動同期・復旧**: ネットワーク断絶後や再ログイン後でも、未受信のメッセージが自動で補完されます。
- **複数端末での通知設定同期**: 通知設定を DB で管理し、複数端末・複数ブラウザ間で設定を一貫して維持します。
- **データベース管理画面 (SQLAdmin)**: 管理者専用のセキュアなWEB画面（`/admin`）から、全テーブル（ユーザー、メッセージ、タスク等）のCRUD操作が可能です。機密情報は非表示に保護されています。

## 2. なぜ「ロスト対策」が必要なのか
一般的な WebSocket 実装には、以下の信頼性に関わる課題が存在します。
- **配信の不確実性**: メッセージ送信の瞬間に受信側が一時的なネットワーク不安定状態にあると、メッセージが消失（ロスト）し、二度と届かない。
- **不透明なロスト**: 消失したこと自体にクライアントが気づけず、画面上の情報が不整合なまま放置される。
- **順序の逆転**: ネットワークの遅延やリトライにより、古い情報が新しい情報の後に届き、ステータスが先祖返りする。

本プロジェクトは、これらの課題を **「DB を唯一の真実のソースとする設計」** によって解決します。

## 3. 実現する仕組み (設計の柱)

### 3.1 信頼性の追求（ロストゼロ & 順序保証）
- **Transactional Outbox**: メッセージ保存と配信フィード（Outbox）の書き込みを同一 DB トランザクションで完結。DB に記録されたデータは、プロセスがクラッシュしても必ず配信されます。
- **厳密連番採番 (Sharded Sequencing)**: スコープ（ルームやユーザー）ごとに、欠番のない連続した整数 ID を発行。
    - **トレードオフ**: 標準的な `SEQUENCE` ではなく行ロック（`UPDATE ... RETURNING`）による採番を行うため、同一スコープ内での書き込みスループットは制限されます（一般的な SSD 環境で秒間数百〜数千件程度）。これは、スコープを細かく分ける（Sharding）ことで水平方向にスケール可能です。
- **クライアント側ギャップ検知**: 受信した ID が `最新ID + 1` でない場合、クライアントが即座にロストを検知。差分取得 API を用いて未受信分を自動的に埋め合わせます。
- **接続・再接続時の即時同期トリガー**: WebSocket の初回接続成功時やネットワーク復旧による再接続時に、30秒間隔の定期ポーリングを待たず即座にデータ同期（`fetchChatMissing` / `fetchRequestMissing`）をトリガー。これにより、待機状態（「待機中...」）から最新同期時刻表示へと遅延なく遷移します。
- **Web Worker によるバックグラウンド心拍の維持**: ブラウザタブが非アクティブ化された際、ブラウザの省電力機能（タイマースロットリング）によって `setTimeout` が遅延し WebSocket が切断されるのを防ぐため、タイマー処理を Web Worker 内で実行。非アクティブ時でも死活監視（Ping/Pong）を正確に維持し、リアルタイムなブラウザ通知を確実に受け取れるようにします。
- **Page Visibility API を利用した即時再接続**: タブがバックグラウンドからアクティブ（`visible`）に復帰した際、もし接続が切れていれば即座に再接続をトリガーし、バックオフタイマーによる待機ラグなしで最新メッセージを同期します。
- **同期処理の排他制御ガード**: 履歴同期の API 呼び出しが並行して実行されるのを防ぐため、`isSyncingRef` による実行中フラグ（排他ガード）を実装。データ取得の重複や sequence_id カウンタの破損を防止します。
- **切断・ログアウト時のステータス初期化**: ログアウト（トークン消去）または明示的な切断時に、UI の同期ステータス表示を `"未同期"` または `"切断"` に適切にクリアします。

### 3.2 パフォーマンスと効率（超低負荷）
- **LISTEN / NOTIFY**: PostgreSQL の pub/sub 機能を利用。新着メッセージが DB に入った瞬間にリレープロセスへ合図を送り、高頻度なポーリングなしに低遅延配信を実現します。
- **SKIP LOCKED**: 複数サーバー実行時も `FOR UPDATE SKIP LOCKED` により重複配信を防止し、スケーラビリティを確保します。

### 3.3 クライアント側のUX向上（楽観的UI / Optimistic UI）
- **即時クリア＆連続入力**: React 19 の `useOptimistic` および `useTransition` を活用し、送信ボタン押下と同時に入力欄を即座にクリアして次の入力を可能にします（送信中の入力ロックを廃止）。
- **送信中メッセージの仮表示**: 送信したメッセージやリクエストは、チャットログやリクエスト一覧の最下部に「透過（opacity: 0.5）」された状態で即座に仮表示されます。
- **シームレスな確定と失敗時の自動復元**: 送信したメッセージやリクエストは、仮表示から実表示へ自動的かつシームレスに切り替わります。送信に失敗した場合は、仮表示が自動で消去され、送信しようとしていたテキストが入力欄に自動復元（ロールバック）されます。

### 3.4 BFF と WebSocket チケット方式によるセキュア認証（XSS 対策）
本システムでは、Zennの記事「『JWT を localStorage に置くな』はなぜ言われるのか、Cookie 回帰までの時系列整理」の設計思想に基づき、ブラウザ上に生の JWT トークンを一切露出させないセキュアな認証システムを実装しています。
- **BFF (Next.js APIルート) によるトークンの隔離**: 
  - ブラウザと BFF 間の通信は、`HttpOnly`, `Secure`, `SameSite=Lax` 属性を持つセッションCookie（`bff_session`。BFF側でAES-256-GCMにより暗号化）で行います。JavaScriptコードからはトークン値を一切読み取れないため、XSSによるトークン窃取を完全に防ぎます。
  - BFF（サーバーサイド）はCookieを復号し、生のアクセストークン（JWT）を取り出して、FastAPIへ `Authorization: Bearer <JWT>` ヘッダーを付与してリクエストをプロキシします。
- **データベースによるリフレッシュトークン管理とRTR (Refresh Token Rotation)**:
  - セッション無効化の確実性を担保するため、リフレッシュトークンはデータベース（`refresh_tokens` テーブル）にハッシュ化して保存・管理します。
  - トークンの更新（リフレッシュ）時には古いリフレッシュトークンをDBから物理削除（DELETE）して使い捨てるRTR方式を採用しています。
  - ログアウトやパスワード変更、アカウント削除時には、DBからトークンレコードを一括削除することで、発行済みのセッションを即座に無効化（キルスイッチ）できます。
- **WebSocket ワンタイム・チケット方式**:
  - WebSocketはNext.jsの標準ルート経由での双方向プロキシが難しいため、使い捨ての接続チケット方式を採用しています。
  - ブラウザは接続直前に BFF の `/api/auth/ws-ticket` から一時チケット（有効期限10秒、使い捨て）を取得します。
  - 取得したチケットを用いて `ws://localhost:8000/ws?ticket=<チケット>` へ直接接続し、FastAPIはRedisに保存されたチケットを検証・即時削除して接続を確立します。これにより、生のトークンをブラウザ側に長期保存することなく安全に双方向通信を開始できます。

### 3.5 データベース管理画面 (SQLAdmin) の導入
開発・運用時にブラウザ上からデータを確認・修正できるよう、Django風の管理画面ライブラリ **SQLAdmin** を導入しました。
- **セキュアな認証ガード**: 環境変数で定義された `ADMIN_USERNAME` / `ADMIN_PASSWORD` を使ったセッション暗号化（Cookie）により、未ログインのアクセスを完全に遮断します。
- **機密情報の表示制御**: セキュリティのため、`UserORM.hashed_password` や `RefreshTokenORM.token_hash` などの機密データは管理画面の表示・編集・詳細確認から除外して保護しています。
- **全テーブルのCRUD対応**: システムで利用する全7つのデータベースモデル（ユーザー、メッセージ、タスク、通知設定、リフレッシュトークン、配信シーケンス、配信フィード）を対象としています。

## 4. システム構成図

```text
フロントエンド（Next.js / TypeScript / Vanilla CSS）
    ↕ WebSocket / REST API
バックエンド（FastAPI / Python）
    ├─ PostgreSQL（Single Source of Truth）
    │   ├── messages / tasks        （永続データ）
    │   ├── delivery_sequences      （厳密連番カウンタ）
    │   └── delivery_feeds          （Outbox 兼 配信ログ）
    └─ Redis（複数インスタンス間ブロードキャスト用）
```

---

## 5. アーキテクチャ設計：Pydantic とドメインモデルの分離

本プロジェクトでは、**Pydantic を HTTP 境界層（入出力 DTO）に限定**し、ドメイン層を Pydantic 非依存に保つ設計を採用しています。


### 設計方針

```
HTTP リクエスト (raw JSON: {"username": "alice"})
    ↓ Pydantic が型・形式を検証
入力 DTO（Pydantic BaseModel — raw Python 型: str, int）
    ↓ to_domain() — 明示的な変換（ドメインルール検証）
Domain Primitive（DomainPrimitive[T], frozen dataclass）
    ↓ Application / Infrastructure 層で処理
出力 DTO（Pydantic BaseModel — raw Python 型: str, int）
    ↑ from_domain() — 明示的な変換
HTTP レスポンス (raw JSON)
```

### ドメインプリミティブ

`DomainPrimitive[T]` は frozen dataclass として定義され、生成時に必ずビジネスルールを検証します。

```python
# domain/primitives/base.py
@dataclass(frozen=True)
class DomainPrimitive(Generic[T]):
    value: T
    def __post_init__(self):
        self.validate()  # 生成時に不変条件を保証

# domain/primitives/primitives.py
class Username(DomainPrimitive[str]):
    def validate(self):
        if not self.value or len(self.value) > 50:
            raise DomainValidationError("...")
```

Pydantic への依存は一切なく、Application / Infrastructure 層でもそのまま使用できます。

### Presentation 層: DTO パターン

**入力 DTO** は raw Python 型でフィールドを定義し、`to_domain()` で Domain Primitive へ変換します。

```python
# presentation/api/auth.py
class LoginRequest(BaseModel):
    username: str   # raw 型
    password: str   # raw 型

    def to_domain(self) -> tuple[Username, Password]:
        return Username(self.username), Password(self.password)
```

**出力 DTO** は `from_domain()` クラスメソッドで Domain Primitive から生成します。

```python
class LoginResponse(BaseModel):
    access_token: str  # raw 型
    token_type: str

    @classmethod
    def from_domain(cls, token: AuthToken) -> "LoginResponse":
        return cls(access_token=token.value, token_type="bearer")
```

**エンドポイント**では `to_domain()` / `from_domain()` を明示的に呼び出します。

```python
@router.post("/token")
async def login(body: LoginRequest, ...) -> LoginResponse:
    username, password = body.to_domain()           # 明示変換
    token = auth_service.login(username, password)  # Domain 層へ
    return LoginResponse.from_domain(token)         # 明示変換
```

### この設計の利点

| 観点 | 効果 |
|------|------|
| ドメイン層の独立性 | Pydantic に依存しないため、API フレームワークを変更しても Domain は無変更 |
| 変換の可視性 | `to_domain()` / `from_domain()` で変換箇所が一目瞭然 |
| Always-Valid | Domain Primitive は生成時に必ず検証済み。無効な状態のオブジェクトは存在しない |
| テスト容易性 | Domain ロジックを Pydantic なしで単体テスト可能 |

---


## 6. あえて実装しないこと（スコープ外）

学習の焦点を「信頼性の高いメッセージング」に絞るため、以下の機能は簡略化しています。
- CSSはLLMまかせ


---

## 開発環境の起動

本プロジェクトでは、DB などのインフラを Docker で、アプリケーション（Frontend/Backend）をローカルで動かす構成を推奨します。

### 1. インフラの起動 (Docker)
PostgreSQL, Redis, pgAdmin を起動します。
```bash
docker-compose up -d postgres redis pgadmin
```
- **pgAdmin**: `http://localhost:5050` (ID: `admin@example.com`, PW: `admin`)

> **注: 命名統一リファクタ後の初回起動**
>
> `direct_request` 機能の entity を `Task` にリネームしたため、テーブル名が `requests` → `tasks` に変わりました。`Base.metadata.create_all` は既存テーブルを drop しないので、旧 DB を引き継ぐ場合は手動で旧テーブル／旧 sequence 行を削除してください。
>
> ```bash
> docker-compose exec postgres psql -U user -d chat_db -c \
>   "DROP TABLE IF EXISTS requests; \
>    DELETE FROM delivery_sequences WHERE name IN ('chat_global', 'requests_global');"
> ```
>
> もしくはボリュームごと初期化:
>
> ```bash
> docker-compose down -v
> docker-compose up -d postgres redis pgadmin
> ```
>
> **注: user_id 移行後のマイグレーション**
>
> 送信者の識別子を一意な `user_id` に移行したため、`messages`, `tasks`, `user_settings` テーブルのスキーマ変更と同時に、`delivery_feeds`（Outbox）の JSONB ペイロード内にも `sender_id` / `recipient_id` が追加されました。
> 既存の DB がある場合は、必ず `alembic upgrade head` を実行してください。既存の JSONB データに対しても自動的に UUID が解決・補完されます。

### 2. バックエンドの起動 (Python)
`backend` ディレクトリでライブラリをインストールし、サーバーを起動します。
```bash
cd backend
uv sync
uv run fastapi dev app/main.py
```
- **API Docs**: `http://localhost:8000/docs`
- **管理画面**: `http://localhost:8000/admin` (環境変数の ID / PW でログイン可能)

### 3. フロントエンドの起動 (Node.js)
`frontend` ディレクトリでパッケージをインストールし、開発サーバーを起動します。
```bash
cd frontend
npm install
npm run dev
```
- **Frontend**: `http://localhost:3000`

---

### その他の起動方法

#### Docker Compose で一括起動
バックエンドも含めて Docker で動かしたい場合（フロントエンドは引き続きローカル起動が必要です）：
```bash
docker-compose up -d --build
```
※ `docker-compose.yml` には現在フロントエンドが含まれていないため、手順 3 は常に必要です。

#### Kubernetes (minikube)
ローカルで k8s クラスタを動かす場合の手順です。

1. **minikube の起動と環境設定**
   ```bash
   minikube start
   # ローカルの Docker デーモンを minikube 内に切り替え
   # (bash の場合)
   eval $(minikube docker-env)
   # (Windows PowerShell の場合)
   minikube docker-env | Invoke-Expression
   # (Windows コマンドプロンプトの場合)
   @FOR /f "tokens=*" %i IN ('minikube -p minikube docker-env --shell cmd') DO @%i
   ```

2. **イメージのビルド**
   ```bash
   # クラスタ内で直接イメージをビルド (backend.yaml で指定されているイメージ名と合わせる必要があります)
   docker build -t chat-backend-ddd:latest ./backend
   ```

3. **リソースの適用**
   ```bash
   # 最初に Secret を適用します
   kubectl apply -f k8s/secret.yaml

   # 各種リソースを適用します
   kubectl apply -f k8s/postgres.yaml
   kubectl apply -f k8s/redis.yaml
   kubectl apply -f k8s/backend.yaml
   ```

4. **サービスの公開**
   ```bash
   minikube service backend
   ```

---

## 開発ガイドライン

### リンター・フォーマッターの実行

#### フロントエンド (Biome)
```bash
cd frontend
npm run lint    # チェック
npm run format  # 修正
```

#### バックエンド (Ruff, MyPy)
```bash
cd backend
uv run ruff check .
uv run ruff format .
uv run mypy .
```

---
