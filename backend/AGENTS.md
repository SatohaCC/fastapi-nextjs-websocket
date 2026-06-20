# FastAPIのルール
- Docstringを必ず実施して。

# 実装完了時に必ず実行するコマンド

実装が終わったら、以下をこのコマンドでテストをパスさせること。

```powershell
powershell -ExecutionPolicy Bypass -File check.ps1
```

# アーキテクチャ設計指針 (Architecture Guidelines)

## 1. 採用パターン: オニオンアーキテクチャ
本プロジェクトでは、変更に強く、テストが容易な **Onion Architecture** を採用する。
中心に「ビジネスロジック（Domain）」を配置し、外部（DB、UI、フレームワーク）への依存を内側に向かって制御する。
