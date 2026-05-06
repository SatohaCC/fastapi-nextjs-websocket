# WebSocket Chat — Outbox + LISTEN/NOTIFY + DDD

学習用リポジトリ：WebSocket のロスト対策と、PostgreSQL を核とした高信頼・低負荷なメッセージング設計を学ぶために作成。

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

## 開発環境の起動

### Docker Compose
最も手軽な起動方法です。
```bash
docker-compose up -d --build
```
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- pgAdmin: `http://localhost:5050`

### Kubernetes (minikube)
ローカルで k8s クラスタを動かす場合の手順です。

1. **minikube の起動と環境設定**
   ```bash
   minikube start
   # ローカルの Docker デーモンを minikube 内に切り替え
   eval $(minikube docker-env)
   ```

2. **イメージのビルド**
   ```bash
   # クラスタ内で直接イメージをビルド（レジストリへの Push 不要）
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
   # Backend サービスをブラウザで開く
   minikube service fastapi-backend
   ```

- **Backend**: `LoadBalancer` 設定により、上記コマンドで払い出される URL でアクセス可能です。

## 6. 最近の改善点
- **チャット同期の安定化**: Relay Worker のレースコンディションを修正し、メッセージ送信直後のリアルタイム更新を確実にしました。
- **ソートロジックの改善**: 履歴メッセージとリアルタイムメッセージの混在時も、シーケンスIDとエンティティIDを組み合わせることで正しい順序を維持するようにしました。
