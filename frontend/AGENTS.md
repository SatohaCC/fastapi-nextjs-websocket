<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## アーキテクチャの基本方針
本プロジェクトは、**Feature-Based Architecture** と **Container/Presentational パターン** を採用し、関心の分離を徹底しています。

### 1. レイヤー構造と役割
- **Page (app/):** ルーティングとデータフェッチの開始点。実態は最上位の Container。
- **Container (features/*/components/*Container.tsx):**
  - 複雑なロジックを持ち、Hooks を呼び出してデータを管理する。
  - Presentational コンポーネントにデータを Props として分配する。
- **Presentational (features/*/components/*.tsx):**
  - 接尾辞なしの名前（例: `LoginForm.tsx`）。
  - ロジックを持たず、受け取ったデータを表示するだけの「純粋な」コンポーネント。
- **Hooks (features/*/hooks/):**
  - `useEffect`, `useState` を用いた状態管理やバックエンドとの通信（API/WebSocket）をカプセル化する。
  - クライアント API を使用する場合は必ず `"use client";` を指定する。
- **API (features/*/api.ts):**
  - エンドポイントへのリクエスト処理を担当する。Hooks からのみ呼び出される。

### 2. ディレクトリ構造
- `src/app/`: ルーティング。
- `src/features/`: 機能単位のコード（UI、Hooks、API）。
- `src/components/ui/`: プロジェクト全体で共有される原子的な UI 部品（Button, Input 等）。
- `src/lib/`: 共通のユーティリティやグローバル設定（`config.ts` 等）。

### 3. インポートルール
- **依存関係の方向:** `app` -> `features` -> `components/ui`
- **UIコンポーネントの独立性:** `src/components/ui/` は `features` や `app` に依存してはならない。
- **機能のカプセル化:** `features` 配下のコンポーネントは、他の機能の内部実装を直接参照せず、公開された Hooks や API を介してやり取りすることが望ましい。

### 4. 命名規則
- **Presentational コンポーネント:** 接尾辞なし（例: `GlobalChat.tsx`）
- **Container コンポーネント:** `Container` 接尾辞（例: `GlobalChatContainer.tsx`）

### 5. スタイリング規約（Panda CSS）
- **スタイルのカプセル化**: 見た目の装飾やスタイル定義は、ad-hoc に Container 側で定義して注入するのではなく、必ず各 Presentational UI コンポーネント（共通UIまたは機能固有UI）の内部、あるいはそのコンポーネント専用のスタイルファイル（`*.styles.ts`）にカプセル化してください。
- **共通UIの整理**: 複数の機能で共有されるUIコンポーネントは `src/components/ui/` 配下の `primitives/` (単体) または `composites/` (複合) に配置します。
- **機能固有UIの配置**: 特定の1つの機能でしか使われないUIコンポーネント（例: `WorkspaceHeader` 等）は、共通UIに置かず、該当する機能フォルダ（`src/features/<feature>/components/`）配下にスタイル定義ファイル（`*.styles.ts`）と共に配置します。
- **機能コンポーネントでのスタイル微調整**: レイアウトの微調整（余白、方向、幅）が必要な場合は、インラインの `css({...})` を使用するか、親のコンテナスタイルからのセレクター制御（例: `& input` や `& button`）に限定します。

### 6. 作業の完了条件
実装完了後は必ず以下のコマンドを実行し、エラーがないことを確認すること。
```bash
npm run test:all
```
※ このコマンドには `lint:fix`, `format`, `type-check`, `test:run` (vitest) が含まれています。
