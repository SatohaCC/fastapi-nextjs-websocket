# FastAPIのルール
- Docstringを必ず実施して。

> backend / frontend をまたぐ命名・構造の規約は [../CONVENTIONS.md](../CONVENTIONS.md) を参照すること。本ドキュメントは backend 固有の運用ルールに絞る。

# 実装完了時に必ず実行するコマンド

実装が終わったら、以下を **この順番で** すべてパスさせること。

```bash
# 1. フォーマット
uv run ruff format .

# 2. リント（自動修正あり）
uv run ruff check . --fix

# 3. 型チェック（mypy）
uv run mypy app/

# 4. 型チェック（pyright）
uv run pyright app/

# 5. テスト
uv run pytest
```

- `ruff format` → コードスタイルの統一
- `ruff check` → import 整理・スタイル違反・未使用変数などの検出
- `mypy` → 型注釈の整合性チェック（ruff では検知できない型エラーを拾う）
- `pyright` → mypy が見逃す厳格な型チェック（Protocol メソッドの `...` 省略・オーバーライドの非互換など）
- `pytest` → ロジックの正しさの検証

5つすべてエラーなしになってから PR を作成すること。

すべてを一括実行する場合は以下のスクリプトを使用すること。

```powershell
powershell -ExecutionPolicy Bypass -File check.ps1
```

# アーキテクチャ設計指針 (Architecture Guidelines)

## 1. 採用パターン: オニオンアーキテクチャ
本プロジェクトでは、変更に強く、テストが容易な **Onion Architecture** を採用する。
中心に「ビジネスロジック（Domain）」を配置し、外部（DB、UI、フレームワーク）への依存を内側に向かって制御する。
