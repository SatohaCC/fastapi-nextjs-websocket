## Version Control — 必須手順

このプロジェクトは **Jujutsu (jj)** でバージョン管理している。詳細なルールは `.claude/rules/jujutsu-rules.md` を参照。

**コード編集を開始する前に、必ず以下の手順を実行すること:**

1. `jj log --ignore-working-copy -r @` で現在の change を確認する
2. description が空かつ diff が空（empty）→ `jj describe -m "<description>"` で description を設定して作業開始
3. それ以外（すでに作業中 or 完了済み）→ `jj new -m "<description>"` で新しい change を作成
4. description は.claude\workflows\commit-message-generator.md を参照して。

**禁止事項:** `git` コマンドの直接使用（`jj git` サブコマンドおよび `gh` CLI は許可）

## Issue 管理

プロジェクトの課題（バグ、改善案、タスク）は **GitHub Issues** で管理する。

- 新しい課題が見つかった場合は、`gh issue create` で GitHub に登録すること。
- ローカルファイル（`ISSUES.md` など）での課題管理は行わない。
- 作業開始前、または作業中に気づいた改善点は積極的に Issue 化して可視化すること。
