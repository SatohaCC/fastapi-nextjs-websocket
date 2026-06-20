# ドキュメント変更ログ（Changelog）

本ファイルは、プロジェクト全体のアーキテクチャ、仕様、機能実装、およびドキュメント構成の主要な更新履歴を時系列で記録するログです。（2026-06-20 の新ドキュメント構成移行後から記録しています）

## 履歴

### [2026-06-21] ユーザー / ユーザー設定 設計仕様の新規作成
*   表示名変更・パスワード変更・アカウント削除・パスワードリセット、通知設定の永続化（`UserSettings`）、アクティブセッション一覧・個別失効を一つのドキュメントに整理した [/okf/docs/user-settings.md](/okf/docs/user-settings.md) を新規作成しました（既存の [/okf/docs/auth.md](/okf/docs/auth.md) はログイン・JWT・WebSocketチケットの認証フローに専念させ、ユーザープロファイル管理はこちらに分離）。

### [2026-06-20] セッション個別削除時の誤ログアウト防止（セッション単位の強制切断への変更）
*   **不具合の原因**: セッション管理画面で特定のセッション（別端末等）を `DELETE /api/auth/sessions/{id}` で削除すると、`revoke_session` が発火する `force_disconnect` イベントが `user_id` のみで識別されており、`ChatManager` が WebSocket 接続を `user_id` 単位（セッション単位ではなく）でしか管理していなかったため、削除対象ではない別の接続（操作中の端末を含む）まで強制切断され、フロントエンドがクローズコード `1008` を検知して誤って強制ログアウトしていました。
*   **修正内容**:
    *   `TicketStore.create_ticket`/`consume_ticket` が `session_id` も保持・返却するように変更し、`/api/auth/ws-ticket` でアクセストークンから取り出した `session_id` をチケットに含めるようにしました（`AuthService.get_session_id_from_token` を新設）。
    *   `get_ws_authenticated_user` が消費した `session_id` を `websocket.state` 経由で `websocket_endpoint` に橋渡しし、`ChatManager.connect` で `WebSocket → session_id` の対応を記録するようにしました。
    *   `ChatManager` に `force_disconnect_session(user_id, session_id)` を新設し、対象セッションに紐づく接続のみをクローズコード `1008` で切断するようにしました（全セッション無効化が正しい `change_password`/`delete_account`/`reset_password` は既存の `force_disconnect_user` のまま維持）。
    *   `AuthService.revoke_session` の `force_disconnect` イベントに `session_id` を含め、`redis_subscriber` がその有無で `force_disconnect_session`／`force_disconnect_user` を呼び分けるようにしました。

### [2026-06-20] 表示名変更後の通知/メッセージ判定不具合の修正とUUIDベースへの完全移行
*   **不具合の原因**:
    *   `useAuth` カスタムフックが呼び出し元コンポーネントごとに個別の状態を持つため、表示名変更フォームで `setSession` を呼んでも、共通レイアウト側の `WorkspaceContext` に渡る表示名が古いままになる同期ズレが発生していました。
    *   グローバルチャット／ダイレクトリクエストの自分自身判定・宛先判定に可変の `username`（表示名）を使用していたため、表示名変更後に判定が崩れていました。
*   **修正内容**:
    *   バックエンド: `MeResponse` に `id`（UUID）を追加し、`GlobalChatPayload`/`GlobalChatServerMessage`/`DirectRequestServerMessage`/`DirectRequestUpdatedServerMessage` に `user_id` / `sender_id` / `recipient_id`（いずれも UUID 文字列）を追加しました。
    *   フロントエンド: `WorkspaceContext` に `id`（UUID）と `updateUsernameState` を追加し、認証状態を一元管理する `useWorkspaceContext` 経由で表示名変更フォーム（`useAccountSettings.ts`）が状態を更新するように変更しました。
    *   `useNotifications.ts` / `useDirectRequest.ts` / `useGlobalChat.ts` の自分自身判定・宛先判定を、すべて不変の UUID（`id` / `sender_id` / `recipient_id`）ベースに変更しました。

### [2026-06-20] 設定画面滞在時の通知受信改善（通知のグローバル化）
*   **修正内容**:
    *   チャットメッセージやダイレクトリクエストを受信した際に通知（トーストおよびブラウザ通知）を処理する `useNotifications` フックが、従来はチャット画面（`Workspace`）内でのみマウントされていたため、設定画面（`/settings`）に遷移すると通知が届かなくなる問題を修正しました。
    *   共通親レイアウト `AuthenticatedLayout` 内の `WorkspaceContext.Provider` 配下に、通知のみをフックする空コンポーネント `NotificationHandler` を新設してマウントしました。これにより、ログイン後のどの画面（設定画面など）に滞在していても常に通知を受け取ることができるようになりました。
    *   不要となった `Workspace.tsx` からの `useNotifications` の呼び出しおよびインポートを削除しました。

### [2026-06-20] 共通ヘッダー導入に伴うレイアウト崩れ・ナビゲーション・画面遷移時の表示リセット問題の修正
*   **修正内容**:
    *   設定詳細画面（表示名変更、パスワード変更、アカウント削除）で共通ヘッダーと独自のヘッダーが重複して描画されていた問題を解消するため、個別フォーム（`ChangePasswordForm`, `ChangeUsernameForm`, `DeleteAccountForm`）から独自ヘッダーを削除し、インラインでのナビゲーション構成に統一しました。
    *   モバイル表示時（画面幅 1024px以下）に共通ヘッダーの高さ分が考慮されていなかったため、`WorkspaceLayout.styles.ts` 内の最小高さを `calc(100vh - 64px)` に変更しました。
    *   利便性向上のため、共通ヘッダーのタイトル（`WebSocket test`）をクリックした際に `/workspace`（チャット画面）に遷移するよう、`Link` コンポーネントで囲み、ホバー時のスタイル（カーソルポインタ、不透明度変化）を適用しました。
    *   **画面遷移時の表示リセットバグ修正**: 共通ヘッダーによる常時接続の維持によって画面遷移（`/workspace` ⇄ `/settings`）時に WebSocketProvider が維持されるようなり、再マウントによる WebSocket 接続の切断/再接続が発生しなくなりました。これに伴い、`useDirectRequest` および `useGlobalChat` の初回マウント時に `isAuthenticated` を検知する `useEffect`（リセット処理）が不要に走って状態が初期化されてしまい、かつ接続状態に変化がないため初期同期APIがトリガーされず、遷移後に表示が消える問題を修正しました。初回マウント時にこの不要な初期化を `useRef(isFirstMount)` によってスキップするよう修正し、遷移後も表示が正しく維持・同期されるようにしました。

### [2026-06-20] ログイン後ページの共通認証レイアウト導入とヘッダーの共通化
*   **修正内容**:
    *   Next.js の Route Group（`(authenticated)`）を導入し、`/workspace` と `/settings`（配下のサブディレクトリ含む）をグループ配下に移動させました。
    *   共通の `(authenticated)/layout.tsx` を新設し、認証ガード、`WebSocketProvider`、`WorkspaceContext.Provider`、および共通ヘッダー（`WorkspaceHeaderContainer`）の描画を一元化しました。これにより、チャット画面と設定画面の遷移（`/workspace` ⇄ `/settings`）時に WebSocket 接続が切断されず、接続状態を維持したままシームレスに遷移できるようになりました。
    *   設定画面（`settings/page.tsx`）から冗長な認証チェックや独自ヘッダーを削除し、コンテンツ領域のみを描画するように簡素化しました。
    *   `Workspace.tsx` および `WorkspaceLayout.tsx` から個別のヘッダー描画指定を削除（および `header` プロパティをオプショナル化）しました。

### [2026-06-20] ソースコードリンクをリポジトリルート絶対パス形式へ統一
*   **課題**: 各設計仕様書のソースコードリンクがドキュメントからの相対パス（`../../backend/...`）で記述されていたため、ドキュメントの配置場所（ディレクトリ階層）が変わるとリンクが一斉に壊れる脆さがありました。
*   **修正内容**:
    *   `auth.md`, `direct-requests.md`, `global-chat.md`, `websocket.md` のソースコードリンクを、リポジトリルートからの絶対パス（`/backend/...`, `/frontend/...`）形式へ統一しました。
    *   [ドキュメント作成基準 (doc-standards.md)](/okf/doc-standards.md) の「リンクの記述ルール」を更新し、ソースコードリンクはルート絶対パス、ドキュメント間リンクは相対パスとする方針を明文化しました。
    *   検証スクリプト `scripts/check_okf.py` を拡張し、`/backend/`・`/frontend/` 始まりのリンクをリポジトリルート起点で解決して実在確認するようにしました（それ以外のルート絶対リンクはエラー扱い）。

### [2026-06-20] OKF インデックスの整理およびドキュメント作成基準（仕様拡張）の定義
*   **課題**: 従来の `okf/index.md` にソースコードファイルへの直接リンク（`task.py` 等）が大量に含まれており、OKF SPECが掲げる「段階的開示（Progressive Disclosure）」の原則に照らして情報が細かすぎる状態となっていました。また、プロジェクト独自のドキュメント構成基準や記述ルールが明文化されていませんでした。
*   **修正内容**:
    *   `okf/index.md` をリファクタリングし、ナレッジバンドル内のコンセプトドキュメントとその概要のみを記載する簡潔なインデックスに整理しました。
    *   プロジェクト独自の仕様書テンプレート、リンクの記述形式（コードリンクは `file:///` 必須、ドキュメント間リンクは相対パス必須）、ライフサイクルルールを明文化した [ドキュメント作成基準 (doc-standards.md)](/okf/doc-standards.md) を新設し、インデックスに登録しました。

### [2026-06-20] 表示名変更時の強制ログアウト防止と WebSocket 自動再接続の実装
*   **課題**: これまで表示名（`username`）の変更時にバックエンドが発行していた `force_disconnect` イベントにより、WebSocket接続がクローズコード `1008` (session_revoked) で強制切断され、フロントエンド側でログアウト処理が走ってしまうUX上の不具合がありました。
*   **修正内容**:
    *   `ConnectionManager` および `ChatManager` に、クローズコード `1000` (Normal Closure) で接続を閉じる `reconnect_user` メソッドを実装しました。これにより、クライアントはセッションを維持したまま自動的に再接続処理（指数バックオフ付き）を走らせるようになります。
    *   Redis Pub/Sub の `session_control` チャンネルで、新イベント `"reconnect"` をハンドリング可能に拡張しました。
    *   `AuthService.update_username` 処理の最後で、従来の `_publish_force_disconnect` の代わりに `_publish_reconnect` を呼び出すように変更しました。
    *   `test_websocket_revocation.py` に、`reconnect_user` のクローズコード `1000` 切断テストおよび Redis `reconnect` メッセージの購読処理テストを追加しました。

### [2026-06-20] 表示名変更後のダイレクトリクエスト配信不具合の修正
*   **不具合の原因**: WebSocketエンドポイントやリカバリAPI、およびルーティング戦略（DirectStrategy）が、ダイレクトリクエストのストリーム名や関係者判定に可変の `username`（表示名）を用いていたため、表示名を変更するとメッセージが届かなくなるバグが発生していました。
*   **修正内容**:
    *   `DirectRequestPayload` および `DirectRequestUpdatePayload` に、不変でユニークな `sender_userid` と `recipient_userid` を追加しました。
    *   シリアライズ処理（`serialization.py`）を更新し、上記フィールドのJSONシリアライズ/デシリアライズを実装（古いDBレコードとの後方互換性のためのフォールバックロジックも追加）。
    *   WebSocketエンドポイント（`endpoint.py`）およびREST API（`feeds.py`）で、ダイレクトリクエストシーケンスの特定と復旧フィード問い合わせに不変な `user.userid` を用いるように修正しました。
    *   ルーティング戦略（`routing_strategies.py`）を修正し、所有者名とペイロードの突き合わせを `userid` ベースで行うようにしました。

### [2026-06-20] 設定画面でのユーザーID変更表記の修正 (表示名変更への修正)
*   **フロントエンドの修正**: `NotificationSettings.tsx` のアカウント設定内のリンク表示を「ユーザーIDの変更」から「表示名の変更」へ修正しました。ユーザーID (`userid`) は読み取り専用であるため、実際の変更対象である表示名 (`username`) に合わせました。
*   **バックエンドの修正**: `auth.py` の `UpdateUsernameRequest` スキーマおよび `update_username` エンドポイントのコメント・docstring が「ユーザーIDの変更」と表記されていたため、実態に合わせて「表示名の変更」へ修正しました。

### [2026-06-20] WebSocket リアルタイム通信設計書の作成
*   **ドキュメント新規作成**: リアルタイム接続管理、ハートビート（Ping/Pong）、自動再接続、チケット認証、および Redis Pub/Sub 配信について解説する `websocket.md` を作成しました。
*   **ナビゲーション更新**: `okf/index.md` のナビゲーションに `websocket.md` のリンクを追加しました。

### [2026-06-20] ナレッジドキュメントの機能ベース再編
*   **ドキュメント構成再編**: アーキテクチャおよびレイヤー中心だった設計書を廃止し、主要3機能（`auth.md`, `direct-requests.md`, `global-chat.md`）の機能単位の設計仕様書へ再編しました。各ファイルにはオニオンアーキテクチャの各レイヤー（Domain, Application, Infrastructure, Presentation）における責務、具体的なソースコードへのリンク、データシーケンス、セキュリティ/信頼性ルールを網羅しています。
*   **ナビゲーション更新**: `okf/index.md` のナビゲーションリンクを更新し、新規の機能ベースのファイル構成を反映しました。

### [2026-06-20] 認証関連ドキュメントの整理と集約
*   **ドキュメント集約・更新**: 重複の多かった `bff-auth-architecture.md` および `refresh-token-implementation-plan.md` を、包括的な `auth-authorization.md`（認証・認可仕様書）にマージしました。「脅威モデルと対策まとめ」「既知の制限と今後の改善案」の項目を追加しました。
*   **ドキュメント削除**: 不要となった `bff-auth-architecture.md` および `refresh-token-implementation-plan.md` を物理削除しました。
*   **ナビゲーション更新**: `index.md` から削除されたファイルのリンクを削除しました。

### [2026-06-20] オニオンアーキテクチャ機能マッピング仕様書の作成
*   **ドキュメント新規作成**: 認証・認可、ダイレクトリクエスト、グローバルチャットの主要3機能がオニオンアーキテクチャのどのレイヤー（Domain, Application, Infrastructure, Presentation）で実装されているかのマッピングを解説する `onion-feature-mapping.md` を作成。
*   **ナビゲーション更新**: `index.md` に新設ドキュメントの相対リンクを追記。
