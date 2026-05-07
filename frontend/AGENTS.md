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
- **CSS Modules:** コンポーネント名と同じ名前（例: `GlobalChat.module.css`）
