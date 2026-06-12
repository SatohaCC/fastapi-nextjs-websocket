import { describe, expect, it, vi } from "vitest";
全体評価
おおむね健全です。トランザクショナル Outbox ＋ ストリーム単位の欠番なし連番 ＋ クライアント側 seq ギャップ検知＋REST 再取得という、教科書的な at‑least‑once 配信＋クライアント冪等化 の構成になっており、主要な経路に多重の安全網があります。ただし復旧窓 24 時間を中心に、いくつか明示すべき穴があります。

仕組みの要約（経路ごと）
採番: delivery_feeds は DeliverySequenceORM のカウンタを同一トランザクション内で行ロック更新（sa_outbox_repository.py:31-57）。ロールバック時はカウンタ増分も巻き戻るため、ストリーム単位で欠番なし → seq ギャップ検知の前提が成立。
配信: Outbox → relay_worker（NOTIFY 起床/10秒フォールバック）→ Redis publish → redis_subscriber → BroadcastStrategy/DirectStrategy → 各 WS。get_pending は FOR UPDATE SKIP LOCKED（L59-71）で多重 relay でも二重処理しない。
差分検知: seqGap.ts が seq > lastId+1 でギャップ判定 → fetchMissing（REST）。
再取得（2系統）:
再接続時: WS が last_chat_id/last_request_id を送り、endpoint.py の _send_initial_data が Outbox から after‑cursor を履歴リプレイ。
稼働中: feeds.py の /api/feeds/*?after_*_id= が Outbox を返す。seq ↔ after_*_id のセマンティクスは一致。
冪等化: mergeById が id で重複排除。at‑least‑once の重複・順序前後・WS再接続replayとREST再取得の二重到着を吸収。
初期ロード（cursor 無し）: messages/tasks の永続テーブルから recent を取得（Outbox ではない）。ws_manager.connect（socket 登録）→ _send_initial_data（スナップショット）の順なので、登録〜スナップショット間の新着は live と重複し dedup で吸収（取りこぼし窓なし）。
健全な点
✅ 欠番なし連番＋ロールバック安全（採番の穴なし）。
✅ at‑least‑once＋id 冪等化で、relay クラッシュ再 publish・commit 順前後・Redis fire‑and‑forget（購読者一時断）を全て Outbox＋gap 復旧で救済。
✅ 初期接続の取りこぼしは「socket 登録→スナップショット」の重複設計で回避。
✅ direct_request も同一パターン（useDirectRequest.ts:70 で checkSeqGap、last_request_id cursor）。ステータス更新は再接続時に get_tasks_for_user（永続）で現状態に再同期。
✅ presence(system) は seq 復旧を持たないが、前回対応のスナップショット方式で代替済み。
✅ 同期中ギャップの取りこぼし再実行（feedSyncRunner.ts の保留ループ）。
リスク・穴（優先度順）
⚠️ [中] 復旧窓が 24 時間で、超過分は永続テーブルへ fallback しない — cleanup_worker が PROCESSED feed を 24h で削除。再接続/REST 復旧はいずれも Outbox 依存。lastChatId を進めたまま 24h 超オフラインだった永続セッションが再接続すると、cursor〜(now‑24h) の feed は消えており get_feeds_after が飛び番を返す → 該当区間が恒久ロスト（messages テーブルには残っているのに復旧経路が見に行かない）。ページ再読込で cursor が null に戻れば messages から recent を引くため実害は限定的だが、「Outbox 保持＝唯一の差分復旧窓」である点は設計上の弱点。
⚠️ [低〜中] get_after が LIMIT 無制限 — L96-124 は order_by(sequence_id) のみで .limit() 無し。古い cursor＋大量履歴で巨大レスポンス（メモリ/転送/レイテンシ）。ページング上限が望ましい。
⚠️ [低] 初期接続のギャップ検知が「重複設計」に暗黙依存 — messages 由来の初期履歴は seq=None（[schemas.py の from_domain は seq 未設定]）のため lastChatId をシードせず、初回 live メッセージは無条件採用（gap 判定されない）。現状は登録→スナップショットの重複で救えているが、その順序が崩れると穴になる。テストで順序を固定保証しておくと安全。
ℹ️ [情報] commit 順の前後で一時的に飛び番 → クライアントが REST 再取得を余計に走らせる（ロストではなく性能・通信の無駄）。許容範囲。
ℹ️ [情報] スケールアウト前提の確認 — relay は SKIP LOCKED で多重対応だが、ChatManager はプロセス内シングルトン。複数バックエンドだと各インスタンスの購読者が自分のローカル socket にのみ broadcast する形なので、Redis fan‑out 設計とは整合（各インスタンスが購読していれば全 socket に届く）。ただし presence ロスター（online_usernames）はプロセスローカルなので、多インスタンス化すると在席が分裂する。現状単一インスタンス前提なら問題なし。
推奨（対応するなら優先度順）
24h 窓の明示と fallback: 差分復旧が Outbox を超えた（飛び番かつ古い cursor）と判定したら、messages/tasks の永続テーブルから再取得するフォールバック経路を追加。少なくとも「復旧不能区間が存在し得る」ことを設計ドキュメントに明記。
get_after にページング上限を入れる（get_pending 同様の limit＋継続取得）。
初期接続の重複保証をテストで固定（socket 登録 → スナップショットの順序、live/履歴の dedup）。
実害の大きさ順では 1（24h 窓）> 2（無制限クエリ）> 3（暗黙依存） です。どれかに着手しますか？（既存テストは backend 125 / front 46 緑のままです。）
