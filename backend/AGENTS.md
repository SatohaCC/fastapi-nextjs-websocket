# FastAPIのルール
- Docstringを必ず実施して。

# 実装完了時に必ず実行するコマンド

実装が終わったら、以下を **この順番で** すべてパスさせること。

```bash
# 1. フォーマット
uv run ruff format .

# 2. リント（自動修正あり）
uv run ruff check . --fix

# 3. 型チェック
uv run mypy app/

# 4. テスト
uv run pytest
```

- `ruff format` → コードスタイルの統一
- `ruff check` → import 整理・スタイル違反・未使用変数などの検出
- `mypy` → 型注釈の整合性チェック（ruff では検知できない型エラーを拾う）
- `pytest` → ロジックの正しさの検証

4つすべてエラーなしになってから PR を作成すること。

# アーキテクチャ設計指針 (Architecture Guidelines)

## 1. 採用パターン: オニオンアーキテクチャ
本プロジェクトでは、変更に強く、テストが容易な **Onion Architecture** を採用する。
中心に「ビジネスロジック（Domain）」を配置し、外部（DB、UI、フレームワーク）への依存を内側に向かって制御する。
