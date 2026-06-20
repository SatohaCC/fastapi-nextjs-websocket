---
okf_version: "0.1"
---

# ナレッジベース & 開発インデックス (OKF Bundle Root)

本ディレクトリは、プロジェクト（FastAPI - Next.js - WebSockets）の設計ドキュメントおよび仕様を管理する OKF (Open Knowledge Format) バンドルのルートです。

---

## 📖 設計仕様書 (Docs)

*   [認証・認可 設計仕様](/okf/docs/auth.md) - BFF認証、JWTセッション、ワンタイムチケット、RTRリフレッシュ、セッション無効化、レートリミット等の設計と実装。
*   [ユーザー / ユーザー設定 設計仕様](/okf/docs/user-settings.md) - ユーザープロファイル（表示名・パスワード変更、アカウント削除、パスワードリセット）、通知設定の永続化、およびアクティブセッション管理の設計と実装。
*   [ダイレクトリクエスト 設計仕様](/okf/docs/direct-requests.md) - ユーザー間でのタスク依頼・ステータス更新、Transactional Outbox、ファンアウト配信、およびギャップ検知と再同期の設計。
*   [グローバルチャット 設計仕様](/okf/docs/global-chat.md) - 全ユーザー向けのリアルタイムチャット配信、メンション補完UI、レートリミット、およびメッセージ永続化の設計。
*   [WebSocket リアルタイム通信 設計仕様](/okf/docs/websocket.md) - WebSocket接続管理、ハートビート、自動再接続、ワンタイムチケット認証、およびRedis Pub/Subによるマルチノード配信設計。

## ⚙️ 管理・リファレンス

*   [ドキュメント作成基準](/okf/doc-standards.md) - 本プロジェクトにおける OKF (Open Knowledge Format) 設計ドキュメントの記述形式、構成テンプレート、および管理ルール。
*   [ドキュメント変更ログ（Changelog）](/okf/log.md) - アーキテクチャの変更やドキュメントの更新履歴。
*   [OKF 仕様書 (SPEC.md)](/okf/SPEC.md) - 本ナレッジベースが準拠している Open Knowledge Format (OKF v0.1) の技術仕様。
