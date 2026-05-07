# WebSocket Chat — Outbox + LISTEN/NOTIFY + DDD

- 学習用リポジトリ：WebSocket のロスト対策と、PostgreSQL を核とした高信頼・低負荷なメッセージング設計を学ぶために作成。
- 細かい学習過程はこっち  [my-1st-WebSocket-fastapi](https://github.com/SatohaCC/my-1st-WebSocket-fastapi)

## 1. 機能一覧
本システムは、リアルタイム性が求められる以下の機能を備えています。
- **グローバルチャット**: 全参加者によるリアルタイムな情報共有。
- **ダイレクトリクエスト**: 特定ユーザー間での依頼・承認ワークフロー。
    - ステータス管理（未着手, 進行中, 完了）が可能。
- **自動同期・復旧**: ネットワーク断絶後や再ログイン後でも、未受信のメッセージが自動で補完されます。

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
- **クライアント側ギャップ検知**: 受信した ID が `最新ID + 1` でない場合、クライアントが即座にロストを検知。差分取得 API を用いて未受信分を自動的に埋め合わせます。

### 3.2 パフォーマンスと効率（超低負荷）
- **LISTEN / NOTIFY**: PostgreSQL の pub/sub 機能を利用。新着メッセージが DB に入った瞬間にリレープロセスへ合図を送り、高頻度なポーリングなしに低遅延配信を実現します。
- **SKIP LOCKED**: 複数サーバー実行時も `FOR UPDATE SKIP LOCKED` により重複配信を防止し、スケーラビリティを確保します。

## 4. あえて実装しないこと（スコープ外）
学習の焦点を「信頼性の高いメッセージング」に絞るため、以下の機能は簡略化しています。
- JWT のトークン更新（Refresh Token）機能。



## 5. システム構成図

```text
フロントエンド（Next.js / TypeScript / Vanilla CSS）
    ↕ WebSocket / REST API
バックエンド（FastAPI / Python）
    ├─ PostgreSQL（Single Source of Truth）
    │   ├── messages / requests     （永続データ）
    │   ├── delivery_sequences      （厳密連番カウンタ）
    │   └── delivery_feeds          （Outbox 兼 配信ログ）
    └─ Redis（複数インスタンス間ブロードキャスト用）
```

---

## 6. アーキテクチャ設計：Pydantic とドメインモデルの分離

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

## 開発環境の起動

本プロジェクトでは、DB などのインフラを Docker で、アプリケーション（Frontend/Backend）をローカルで動かす構成を推奨します。

### 1. インフラの起動 (Docker)
PostgreSQL, Redis, pgAdmin を起動します。
```bash
docker-compose up -d postgres redis pgadmin
```
- **pgAdmin**: `http://localhost:5050` (ID: `admin@example.com`, PW: `admin`)

### 2. バックエンドの起動 (Python)
`backend` ディレクトリでライブラリをインストールし、サーバーを起動します。
```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```
- **API Docs**: `http://localhost:8000/docs`

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
   eval $(minikube docker-env)
   ```

2. **イメージのビルド**
   ```bash
   # クラスタ内で直接イメージをビルド
   docker build -t fastapi-nextjs-websocket-backend ./backend
   ```

3. **リソースの適用**
   ```bash
   kubectl apply -f k8s/postgres.yaml
   kubectl apply -f k8s/redis.yaml
   kubectl apply -f k8s/backend.yaml
   ```

4. **サービスの公開**
   ```bash
   minikube service fastapi-backend
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
poetry run ruff check .
poetry run ruff format .
poetry run mypy .
```
