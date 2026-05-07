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

## Version Control — 必須手順

このプロジェクトは **Jujutsu (jj)** でバージョン管理している。詳細なルールは `.claude/rules/jujutsu-rules.md` を参照。

**コード編集を開始する前に、必ず以下の手順を実行すること:**

1. `jj log --ignore-working-copy -r @` で現在の change を確認する
2. description が空かつ diff が空（empty）→ `jj describe -m "<description>"` で description を設定して作業開始
3. それ以外（すでに作業中 or 完了済み）→ `jj new -m "<description>"` で新しい change を作成
4. description は.agents\workflows\commit-message-generator.md を参照して。

**禁止事項:** `git` コマンドの直接使用（`jj git` サブコマンドおよび `gh` CLI は許可）

## Issue 管理

プロジェクトの課題（バグ、改善案、タスク）は **GitHub Issues** で管理する。

- 新しい課題が見つかった場合は、`gh issue create` で GitHub に登録すること。
- ローカルファイル（`ISSUES.md` など）での課題管理は行わない。
- 作業開始前、または作業中に気づいた改善点は積極的に Issue 化して可視化すること。
