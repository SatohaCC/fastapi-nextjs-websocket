## AGENTS.md
編集箇所によって下記を参照すること。
- frontend/AGENTS.md
- backend/AGENTS.md


## Version Control — 必須手順

このプロジェクトは **Jujutsu (jj)** でバージョン管理している。詳細なルールは `.claude/rules/jujutsu-rules.md` を参照。

**コード編集を開始する前に、必ず以下の手順を実行すること:**

1. `jj log --ignore-working-copy -r "@"` で現在の change を確認する
2. description が空かつ diff が空（empty）→ `jj describe -m "<description>"` で description を設定して作業開始
3. それ以外（すでに作業中 or 完了済み）→ `jj new -m "<description>"` で新しい change を作成
4. description は `.claude\workflows\commit-message-generator.md` を参照すること。
5. 関連する Issue がある場合は、description の末尾に `(fixes #<issue-number>)` を含めること。

**禁止事項:** `git` コマンドの直接使用（`jj git` サブコマンドおよび `gh` CLI は許可）

## 作業の終わりに やること
- テストの実行（フロントエンドの場合は `npm run test:all` を実行すること）
- README の更新
- ソースコード内のドキュメントの更新

## Issue 管理

プロジェクトの課題（バグ、改善案、タスク）は **GitHub Issues** で管理する。

- 新しい課題が見つかった場合は、`gh issue create` で GitHub に登録すること。
- ローカルファイル（`ISSUES.md` など）での課題管理は行わない。
- 作業開始前、または作業中に気づいた改善点は積極的に Issue 化して可視化すること。

## PR (Pull Request) ルール

1. **トピックブックマークの使用**: 実装が完了したら `jj bookmark create <name> -r "@"` で意味のある名前のブックマークを作成すること。
2. **GitHub CLI での作成**: PR の作成には `gh pr create --base main --head <name>` を使用すること。
3. **マージ戦略**:
    - 特段の指示がない限り、ベースブランチは `main` とする。
    - **squash は行わないこと**。各 change の履歴を維持したままマージする。
4. **Issue との紐付け**: PR の説明文に、対応する Issue 番号を記載すること（例: `fixes #34`）。
