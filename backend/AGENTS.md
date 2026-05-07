# FastAPIのルール
- Docstringを必ず実施して。

# アーキテクチャ設計指針 (Architecture Guidelines)

## 1. 採用パターン: オニオンアーキテクチャ
本プロジェクトでは、変更に強く、テストが容易な **Onion Architecture** を採用する。
中心に「ビジネスロジック（Domain）」を配置し、外部（DB、UI、フレームワーク）への依存を内側に向かって制御する。
