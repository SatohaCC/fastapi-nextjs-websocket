---
type: Reference
title: ドキュメント作成基準 (Documentation Standards)
description: 本プロジェクトにおける OKF (Open Knowledge Format) 設計ドキュメントの記述形式、構成テンプレート、および管理ルール。
tags: [okf, documentation, standards, templates]
timestamp: 2026-06-20T17:35:00Z
---

# ドキュメント作成基準 (Documentation Standards)

本ドキュメントは、プロジェクト内の設計仕様およびアーキテクチャの記述様式を統一するための、独自の OKF (Open Knowledge Format) ドキュメント記述基準と構成テンプレートを定義します。

---

## 1. 基本的な記述ルール

1. **ファイル配置と命名規則**:
   - 仕様ドキュメントはすべて `okf/docs/` ディレクトリ配下に配置します。
   - 例外として、本基準書などの全体に関わる共通リファレンスは `okf/` 直下に配置します。
   - ファイル名は `kebab-case`（例: `doc-standards.md`, `direct-requests.md`）を使用します。

2. **フロントマターの必須定義**:
   - 予約ファイル（`index.md`, `log.md`）を除くすべてのドキュメントに、以下のYAMLフロントマターを必須とします：
     ```yaml
     ---
     type: Feature Design Specification  # または Reference, Guideline 等
     title: ドキュメントの日本語表示名
     description: 1行の概要文（index.md で表示される説明文と一致させること）
     tags: [関連タグ1, 関連タグ2]
     timestamp: 2026-06-20T17:35:00Z    # 最終更新日時 (ISO 8601)
     ---
     ```

3. **リンクの記述ルール**:
   - **すべての内部リンク（ドキュメント間およびソースコードリンク）**: ローカルマシン固有の絶対パス（`file:///c:/Users/...` など）の露出を防ぎつつ、ファイルの配置場所が変わってもリンクが壊れないようにするため、必ず**リポジトリルートからの絶対パス（`/okf/...`, `/backend/...`, `/frontend/...` 始まり）**で記述します。
   - 検証スクリプトはこの形式のリンクをリポジトリルート起点で解決し、ファイルの実在を確認します。ドキュメントからの相対パス（`./` や `../` 始まり）によるリンクは禁止されています（検証スクリプトでエラーとなります）。
     *ドキュメント間リンクの例:* `[認証設計書](/okf/docs/auth.md)`
     *ソースコードリンクの例:* `[task.py](/backend/app/domain/entities/task.py)`

---

## 2. 標準構成テンプレート (Feature Design Specification)

主要機能の設計ドキュメント（`type: Feature Design Specification`）は、原則として以下の3セクション構成で記述します。

### セクション 1: オニオンアーキテクチャの各レイヤーにおける実装
機能がオニオンアーキテクチャのどのモジュールで実装されているかを、レイヤー（Domain, Application, Infrastructure, Presentation）ごとに整理し、ソースコードリンク付きで列挙します。

### セクション 2: データの流れと設計 (Data Flow & Architecture)
データの状態遷移、API通信、およびコンポーネント間の連携フローを記述します。プロセスの相互作用が複雑な場合は、必ず Mermaid の `sequenceDiagram` または `graph` を用いて視覚化します。

### セクション 3: 信頼性・セキュリティ・制限ルール (Reliability & Resiliency)
機能の堅牢性を担保するための具体的なルールを定義します。
- 順序保証・ロスト対策（シーケンス採番、ギャップ検知など）
- レートリミット制限値
- トークン・クッキー・暗号化などのセキュリティ対策
- 異常系（瞬断、タイムアウト）発生時のハンドリングポリシー

---

## 3. ドキュメントの運用ライフサイクル

1. **ドキュメント新規作成・変更時**:
   - `python scripts/check_okf.py`（または `backend/check.ps1`）を実行し、OKF適合性チェックをパスすることを確認します。
   - ルートの `okf/index.md` に追加ドキュメントへのリンクと概要（`description` と同一の文字列）を追記します。
   - 変更内容を `okf/log.md` の最上部に時系列で追記します。

2. **コード変更との同期**:
   - 実装内容の変更によってアーキテクチャやデータの流れに変更が生じた場合、コード編集の差分（Change）と同時にドキュメントも更新します。
