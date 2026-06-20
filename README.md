# WebSocket Chat — Outbox + LISTEN/NOTIFY + DDD

WebSocketのロスト対策と、PostgreSQLを核とした高信頼・低負荷なメッセージング設計を学ぶ学習用リポジトリです。

機能としては２つ用意しています
- グローバルチャット ：全員参加のチャット
- ダイレクトリクエスト：特定のユーザーへの依頼


PostgressやRedisを冗長化しても動作するコードとしてます。

---

## 📖 設計・仕様ドキュメント (OKF)

本プロジェクトの設計仕様、アーキテクチャ、セキュリティ、および信頼性（ロストゼロ設計）の詳細は、**Open Knowledge Format (OKF)** に準拠したドキュメントとして整理されています。

まずは以下を参照してください。

*   **[OKF ナレッジインデックス](/okf/index.md)**
    *   認証・認可設計（BFF、RTRリフレッシュトークン、ワンタイムチケット等）
    *   ダイレクトリクエスト（タスク依頼）設計（Transactional Outbox等）
    *   グローバルチャット設計（LISTEN/NOTIFY等）
    *   WebSocket リアルタイム通信設計（ハートビート、自動再接続等）
    *   ドキュメント作成基準（仕様書記述ルール等）

---

## ⚙️ ディレクトリ構造

```text
.
├── okf/            # OKF 準拠の設計仕様・ドキュメント群
├── backend/        # FastAPI バックエンドコード
├── frontend/       # Next.js フロントエンドコード
├── terraform/      # 本番デプロイ用の AWS/Terraform テンプレート
└── scripts/        # 開発支援ユーティリティスクリプト
```

---

## 🚀 開発環境の起動

本プロジェクトでは、データベースなどのインフラを Docker で、アプリケーション（Frontend/Backend）をローカルで動かす構成を推奨します。

### 1. インフラの起動 (Docker)
PostgreSQL, Redis, pgAdmin を起動します。
```bash
docker-compose up -d postgres redis pgadmin
```
*   **pgAdmin**: `http://localhost:5050` (ID: `admin@example.com`, PW: `admin`)
*   ※ データベースボリュームをクリーンな状態に初期化したい場合は `docker-compose down -v` を実行してください。

### 2. バックエンドの起動 (Python)
`backend` ディレクトリで依存関係をインストールし、サーバーを起動します。
```bash
cd backend
uv sync
uv run fastapi dev app/main.py
```
*   **API ドキュメント**: `http://localhost:8000/docs`
*   **管理画面 (SQLAdmin)**: `http://localhost:8000/admin` (環境変数で設定された管理者ID/PWでログイン可能)

### 3. フロントエンドの起動 (Node.js)
`frontend` ディレクトリでパッケージをインストールし、開発サーバーを起動します。
```bash
cd frontend
npm install
npm run dev
```
*   **フロントエンド**: `http://localhost:3000`

---

## 🏗️ 本番デプロイ (AWS)

本番デプロイはAWSなどで冗長化を想定します。
詳細な手順やコストの見積もりは、[terraform/README.md](/terraform/README.md) を参照してください。

---

## ✅ 品質チェック・検証

品質と OKF の適合性を維持するため、以下のコマンドで一括チェックおよびテストが可能です。

### バックエンドの一括検証 (チェック＆テスト)
`backend` ディレクトリで以下のスクリプトを実行すると、OKFドキュメント検証、Ruffによるフォーマットとリント、Mypy/Pyrightによる型チェック、および `pytest` による全ユニット/統合テストが実行されます。

```powershell
# Windows (PowerShell)
cd backend
pwsh .\check.ps1
```


### フロントエンドの一括検証 (チェック＆テスト)
`frontend` ディレクトリで以下のスクリプトを実行すると、Biomeによるコードチェックとフォーマット、TypeScriptによる型チェック、および Vitest によるテストが一括で実行されます。

```powershell
# Windows (PowerShell)
cd frontend
npm run test:all
```
