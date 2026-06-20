# Jujutsu (jj) Rules for AI Agents

Jujutsu (jj) をバージョン管理に使用する。**`git` コマンドは原則禁止**（`jj git`, `gh` は許可）。

## 1. 根幹概念と Git 差分マッピング

* **自動保存**: ステージング（`git add`）は存在しない。ファイル保存＝即時反映。
* **用語変遷**: `commit` ➔ **`change`** (ID不変/内容可変) ｜ `branch` ➔ **`bookmark`** ｜ `HEAD` ➔ **`"@"`**
* **コンフリクト**: 発生しても処理は中断せず、未解決状態のまま change に記録される。
* **安全担保**: 全操作は operation log に記録。**`jj undo`** でいつでも直前操作を取り消せる。

---

## 2. 必須コマンドルール

### ⚠️ 読み取り操作（スナップショット抑止）

ファイル変更を伴わない調査では、競合防止のため必ず **`--ignore-working-copy`** を付与する。

> ※直前にファイル作成・編集・削除を行った場合のみ、付与せずに最新状態を反映させる。

### ⚠️ 差分出力（Gitフォーマット化）

AIの解析精度向上のため、差分確認時は**必ず `--git**` を付ける。

* `jj diff --git` （変更直後の確認）
* `jj diff --git --ignore-working-copy -r "@-"` （1つ前のchangeの確認）

---

## 3. 基本ワークフロー・コマンド集

### 状態確認・作業開始

```bash
jj status                         # 変更操作（rebase/squash等）の直後は【必ず】実行しconflictを検知する
jj log --ignore-working-copy      # 履歴グラフ確認

# 作業開始判断: "@" の description/diff が空なら describe、それ以外は new
jj describe -m "feat: <msg>"      # 現changeが空の場合 (Conventional Commits形式/英語)
jj new -m "feat: <msg>"           # すでに作業中の場合

```

### ブックマーク・履歴操作

```bash
jj bookmark create <name> -r "@"   # ブックマーク作成（自動追従しないため手動で動かす）
jj bookmark move <name> -t "@"     # 既存ブックマークの移動
jj abandon "@"                    # 現在の change を破棄
jj workspace update-stale         # 「The working copy is stale」エラー時の同期

```

### 変更の分割・復元

```bash
jj split -r <revision>            # change の分割
jj restore --from <revision> <path> # 特定ファイルの復元
jj evolog --ignore-working-copy -r <change-id>     # change の変遷履歴確認
jj restore --from <change-id>/1 --to <change-id>   # 1つ前の状態に復元 (/0が最新, /1が1つ前)

```

### コンフリクト解決

`jj status` で検知後、対象ファイル内のマーカー（`<<<<<<<` ➔ `%%%%%%%` ➔ `+++++++` ➔ `>>>>>>>`）を直接編集・保存する（`add` 不要）。

---

## 4. 主要 revset (リビジョン指定)

| 記法・パターン | 意味・用途 |
| --- | --- |
| `"@"` / `"@-"` | 現在の change / 1つ前の change |
| `main.."@"` / `trunk().."@"` | main(基底) から現在までの全 change スタック |
| `conflict()` | コンフリクトが発生している change |
| `mine() & mutable() & ~empty()` | 自分の作業中かつ内容のある change 一覧 |

---

## 5. PR 作成ワークフロー

1. **確認不要の原則**: ターゲットは常に `main`。squash（複数 change の統合）は追跡性維持のため**絶対禁止**。
2. **手順**:

```bash
jj git fetch
jj bookmark create feat/issue-<num> -r "@"   # トピックブックマーク作成
jj bookmark track feat/issue-<num>@origin    # 追跡開始
jj git push -b feat/issue-<num>              # リモートへpush
gh pr create --base main --head feat/issue-<num>

```
