## AGENTS.md

## ⚠️ 最重要：ローカル絶対パス（ルートより上の階層）の露出禁止ルール

このプロジェクトでは、開発PCのプライバシー保護および流出防止のため、**リポジトリルートより上の階層を含むローカル絶対パス（例: `C:\Users\...\`）をいかなる場所にも出力・記述・記録してはならない。**

- **チャットレスポンス・ドキュメント・コミットメッセージ**: ファイルパスを言及・記述する際は、必ずリポジトリのルートディレクトリからの相対パス（例: `backend/app/main.py`）、またはルートからの絶対パス（例: `/backend/app/main.py`）で記述すること。
- **リンクの記述**: Markdownリンクにおいても、`file:///C:/Users/...` 形式は絶対パスを露出させるため使用せず、リポジトリ内の相対パス（例: `[main.py](./backend/app/main.py)`）またはリポジトリルート基準のパスを使用すること。
- **ツール実行時の引数**: ツールの引数として絶対パスが必要な場合は、ツール呼び出しパラメータとしてのみ使用し、ユーザーに見えるチャットのテキストやログ、ファイル内容には絶対に書き込まないこと。

## ⚠️ 最重要：開発前のナレッジベース参照ルール

開発や修正を開始する前に、必ず [okf/index.md](okf/index.md)（Open Knowledge Format ナレッジインデックス）を参照すること。
このファイルには、各機能（認証、ダイレクトリクエスト、グローバルチャット、WebSocket）に対応する具体的なソースコードのファイルパスが整理して記載されています。
最小限のファイル検索で実装に入るため、またアーキテクチャの境界を正しく守るために、必ず最初に目を通すこと。

---

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

## 作業の終わりにやること
- テストの実行
- README.md の更新
- okf/のドキュメントの更新

## ドキュメント管理ルール (Open Knowledge Format)

本プロジェクトの `okf/` ディレクトリ配下のドキュメントは、**Open Knowledge Format (OKF v0.1)** に準拠して管理されている。記述形式・テンプレート・運用ルールの詳細は [okf/doc-standards.md](okf/doc-standards.md) を参照すること。

### ルール
1. **フロントマターの要件**: 予約ファイル（`index.md`, `log.md`）を除き、すべての `.md` ファイルの先頭に、`type` フィールドを含む YAML フロントマター（`---` で囲まれたブロック）を必須とする。
2. **リンクの記述**:
   - **ドキュメント間リンク**: OKF ビジュアライザーで関係グラフを正しくレンダリングさせるため、必ず**ドキュメントからの相対パス**（`./` または `../` 始まり）で記述する。
   - **ソースコードへのリンク**: ローカル絶対パス（`file:///...`）の露出を防ぐため、必ず**リポジトリルートからの絶対パス**（`/backend/...` または `/frontend/...` 始まり）で記述する。
3. **検証スクリプトの実行**: ドキュメントを追加・更新した際は、必ずプロジェクトルートで検証スクリプト `python scripts/check_okf.py` を実行して適合性を確認すること。（※ バックエンドの `check.ps1` でも自動検証される）

## Issue 管理

プロジェクトの課題（バグ、改善案、タスク）は **GitHub Issues** で管理する。

- 新しい課題が見つかった場合は、`gh issue create` で GitHub に登録すること。
- ローカルファイル（`ISSUES.md` など）での課題管理は行わない。
- 作業開始前、または作業中に気づいた改善点は積極的に Issue 化して可視化すること。

## PR (Pull Request) ルール

1. **トピックブックマークの使用**: 実装が完了したら `jj bookmark create <name> -r "@"` で意味のある名前のブックマークを英数字（ケバブケース推奨、例: `feat/common-header`）で作成すること。
2. **GitHub CLI での作成**: PR の作成には `gh pr create --base main --head <name>` を使用すること。
3. **言語設定**: PR のタイトルおよび説明文（Body）は必ず**日本語**で書くこと。
4. **マージ戦略**:
    - 特段の指示がない限り、ベースブランチは `main` とする.
    - **squash は行わないこと**。各 change の履歴を維持したままマージする。
5. **Issue との紐付け**: PR の説明文に、対応する Issue 番号を記載すること（例: `fixes #34`）。

<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: このプロジェクトはバージョン管理に Jujutsu (jj) を使用し、`git` コマンドの直接使用は禁止（[jujutsu-rules.md](.claude/rules/jujutsu-rules.md) 参照）。`rtk` の `git` サブコマンド用フィルタは jj には対応していないため使用しないこと。GitHub CLI (`gh`) コマンドにのみ `rtk` を付与する：

```bash
# ❌ Wrong（git 直接コマンドは禁止）
git add . && git commit -m "msg" && git push

# ❌ Wrong（rtk git は jj 運用と無関係）
rtk git status

# ✅ Correct（jj コマンドはそのまま、gh のみ rtk を付与）
jj status
rtk gh pr view <num>
```
