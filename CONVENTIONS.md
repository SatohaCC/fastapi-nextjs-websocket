# CONVENTIONS

このプロジェクトに新規参加した人が、最初に読むべき**命名・構造の単一参照ドキュメント**。
backend (FastAPI / Onion Architecture) と frontend (Next.js / Feature-Based Architecture) を貫く規約を集約している。レイヤー個別の詳細は [backend/AGENTS.md](backend/AGENTS.md) / [frontend/AGENTS.md](frontend/AGENTS.md) を参照。

---

## 1. 命名規則 早見表 (cheatsheet)

| Suffix / Prefix | レイヤー / 場所 | 用途 | 例 |
|---|---|---|---|
| `*ClientMessage` | `backend/app/presentation/websockets/`, `frontend/src/types/ws.ts` | WebSocket: **クライアント → サーバー** の inbound 電文 | `GlobalChatClientMessage` |
| `*ServerMessage` | 同上 | WebSocket: **サーバー → クライアント** の outbound 電文 | `GlobalChatServerMessage` |
| `*Request` | `backend/app/presentation/api/` | REST: リクエストボディ DTO | `SendDirectRequestRequest` |
| `*Response` | `backend/app/presentation/api/` | REST: レスポンス DTO | `DirectRequestResponse` |
| `*Payload` | `backend/app/application/outbox/` | DeliveryFeed に乗る **内部イベントペイロード** (REST の Body ではない) | `DirectRequestPayload` |
| `*Service` | `backend/app/application/services/` | アプリケーションサービス | `DirectRequestService` |
| `*Repository` | `backend/app/domain/repositories/` (interface), `backend/app/infrastructure/persistence/` (impl) | リポジトリ。実装は `SqlAlchemy*Repository` | `TaskRepository`, `SqlAlchemyTaskRepository` |
| `Draft*` | `backend/app/domain/entities/` | 永続化前のエンティティ (Command 側、id 未割り当て) | `DraftTask`, `DraftMessage` |
| `*Container` | `frontend/src/features/*/components/` | ロジックを持つ Container コンポーネント | `GlobalChatContainer.tsx` |
| (suffix なし) | 同上 | 純粋な Presentational コンポーネント | `GlobalChat.tsx` |
| `{Component}Props` | 同上 | コンポーネントの Props 型 (named export) | `export interface GlobalChatProps { ... }` |

### `*Payload` が **REST には使われない** ことに注意
- `*Payload` は「DeliveryFeed のイベント本体」専用 (`backend/app/application/outbox/payload.py` 参照)
- REST のリクエストボディは必ず `*Request`
- これは混同を防ぐための「同じ単語を別レイヤーで重ねない」ルール

---

## 2. snake_case / camelCase の境界

| 場所 | ケース |
|---|---|
| REST URL のパスパラメータ (`/api/direct_requests/{task_id}/status`) | **snake_case** |
| REST クエリ・リクエストボディの field 名 | **snake_case** |
| WebSocket JSON の field 名・`"type"` 値 | **snake_case** |
| Python 内部の identifier | snake_case |
| TypeScript 内部の identifier | camelCase |
| TypeScript の interface field 名 (wire と一致が必要なもの) | **snake_case** (例: `created_at`, `is_history`, `task_id`) |
| MSW handler のパスパラメータ (`:task_id`) | **snake_case** (実 backend に揃える) |

### 原則
- **wire format は snake_case で統一する**。Python と JSON は素直、TypeScript は interface の field 名を spread して受ければ済む
- 変換は frontend 側のローカル変数命名で吸収する (例: `task_id` を受け取って内部では `taskId` に詰め替えるのは OK、wire には snake で書く)

---

## 3. Feature 境界 (frontend)

### `features/{name}/api.ts` の責任
- その feature が呼ぶ **REST エンドポイント関数のみ** を置く
- 他 feature が使う関数を「ついで」で置かない

### cross-feature な fetch の扱い
- `fetchFeeds` のような複数 feature のデータを返すエンドポイントは、**実体の所有者** (= `features/websocket/api.ts`) に置く
- WebSocket 同期は WS feature の責任なので、他 feature がそれを import するのは正常

### feature 内部参照ルール
- ある feature から別 feature の `components/`, `hooks/` を直接 import してはならない
- 共有して良いのは `types/` (主に `@/types/ws`) と `lib/`, `utils/` の global 部品のみ

---

## 4. ディレクトリ配置ルール (frontend)

| パス | 用途 | 例 |
|---|---|---|
| `src/lib/` | 環境変数・グローバル定数・SDK 初期化 | `config.ts` (API_BASE, WS_URL) |
| `src/utils/` | **domain 非依存・feature 非依存**の純粋関数 | `date.ts` (formatDateTime) |
| `src/features/{name}/utils/` | その feature 内でしか使わないヘルパー | `features/websocket/utils/mergeById.ts` |
| `src/components/ui/` | 原子的な UI 部品 (button, badge 等) | `Button.tsx`, `Card.tsx` |
| `src/types/` | wire の型 (両 feature が参照) | `ws.ts` |

**昇格ルール**: `features/{a}/utils/x.ts` が `features/{b}/` でも必要になった瞬間、`src/utils/` に移動する。コピペで複製しないこと。

---

## 5. Container / Presentational パターン

[frontend/AGENTS.md](frontend/AGENTS.md) 第 4 節を要約:

- **Presentational**: suffix なし (`GlobalChat.tsx`)、ロジック無し、props のみで描画
- **Container**: `Container` suffix (`GlobalChatContainer.tsx`)、hooks 呼び出しと state 管理
- **Hooks**: `features/{name}/hooks/` に置き、クライアント API を呼ぶものは `"use client";` を必ず宣言
- **API**: `features/{name}/api.ts` に集約、hooks からのみ呼び出す

### Props 型は named export
匿名の `interface Props` は禁止。代わりに:

```tsx
// frontend/src/features/global_chat/components/GlobalChat.tsx
export interface GlobalChatProps {
  messages: GlobalChatServerMessage[];
  onSend: (text: string) => void;
}

export function GlobalChat({ messages, onSend }: GlobalChatProps) { ... }
```

理由: テスト・Storybook・他コンポーネントからの再利用で Props 型を import できるようにするため。

---

## 6. `Task` と `DirectRequest` のセマンティクス

このプロジェクトには次の意味的マッピングがある:

| 概念 | レイヤー | 名前 |
|---|---|---|
| 内部のエンティティ (汎用的な作業単位) | domain | **`Task`** / `DraftTask` |
| ユーザー向け業務用語 (ダイレクトに送られる依頼) | presentation, application service | **`DirectRequest`** |

そのため:
- `DirectRequestService.send_request(...)` は内部で `Task` エンティティを生成 / 永続化する
- `TaskRepository` は内部実装。ビジネスドメインの外部 (API クライアント等) からは `DirectRequest*` の名前でアクセスする

これは「ドメインモデルの再利用可能な汎用名」と「ユーザー向けの具体的名前」を意図的に分けた設計であり、リファクタリング対象ではない。docstring でこの対応を明示する。

---

## 7. 実装完了時のチェック

### backend
[backend/AGENTS.md](backend/AGENTS.md) 参照。要点:

```powershell
powershell -ExecutionPolicy Bypass -File check.ps1
```

これで `ruff format`, `ruff check --fix`, `mypy`, `pyright`, `pytest` を一括実行する。

### frontend
[frontend/AGENTS.md](frontend/AGENTS.md) 参照。要点:

```bash
npm run test:all
```

これで `lint:fix`, `format`, `type-check`, `test:run` (vitest) を一括実行する。

---

## 8. 適用しない場面 (Conventions の例外)

このドキュメントは「これに従うと迷わない」ためのもので、教条的に守る必要はない。次のような場合は逸脱して良い:

- 外部ライブラリ・フレームワークの命名にどうしても従う必要がある場合 (FastAPI の `Depends` 等)
- wire format のフィールド名が外部仕様で固定されている場合
- 既存コードの破壊的変更コストが学習価値を上回る場合 (議論の上で残す判断もあり)

逸脱する場合は、その判断を docstring / コードコメント / PR description のいずれかに残すこと。

---

## 関連ドキュメント

- [backend/AGENTS.md](backend/AGENTS.md) — backend のレイヤー設計・実装完了コマンド
- [frontend/AGENTS.md](frontend/AGENTS.md) — frontend の Container/Presentational パターン詳細
- [.claude/rules/jujutsu-rules.md](.claude/rules/jujutsu-rules.md) — `jj` を使った VCS ワークフロー
