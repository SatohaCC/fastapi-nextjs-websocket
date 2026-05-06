# WebSocket 信頼性向上・ロスト対策 実装仕様書

本プロジェクトで採用している、通信切断やメッセージの抜け漏れを防ぐための技術仕様と実装箇所のまとめです。

---

## 1. 接続の安定化 (Connection Stability)

通信が不安定な環境でも接続を維持し、切断された場合に安全に復旧するための仕組みです。

| 機能 | 内容 | 主な実装ファイル |
| :--- | :--- | :--- |
| **ハートビート (Ping/Pong)** | サーバーからの定期信号（Ping）を確認。途絶えたら異常とみなし再接続。 | **BE**: `backend/src/presentation/websockets/endpoint.py`<br>**FE**: `frontend/src/features/websocket/hooks/useWebSocket.ts` |
| **指数バックオフ再接続** | 1, 2, 4, 8...秒と待機時間を増やしながら再接続試行し、サーバー負荷を抑制。 | **FE**: `frontend/src/features/websocket/hooks/useWebSocket.ts` (`scheduleReconnect`) |
| **ネットワーク監視** | `navigator.onLine` 等を使い、オフライン時は待機、復帰時に即座に接続。 | **FE**: `frontend/src/features/websocket/hooks/useWebSocket.ts` (`useEffect`) |
| **ステートレスなHooks** | useCallback/useRef を駆使し、画面更新による不必要な切断を防止。 | **FE**: `frontend/src/features/websocket/hooks/useWebSocket.ts` |

---

## 2. メッセージロスト対策 (Data Consistency)

通信瞬断などで「特定のメッセージだけが届かなかった」事態を検知し、自動補完する仕組みです。

| 機能 | 内容 | 主な実装ファイル |
| :--- | :--- | :--- |
| **グローバル連番 (seq)** | Redis の `INCR` を使い、全メッセージに欠番のない連番を付与。 | **BE**: `backend/src/infrastructure/messaging/redis_publisher.py` |
| **ギャップ検知** | 受信したメッセージの `seq` が前回 + 1 でない場合に「抜け」を検知。 | **FE**: `frontend/src/features/websocket/handlers/messageHandlers.ts` |
| **自動ギャップ補完** | 抜けを検知した瞬間、REST API を叩いて不足分のメッセージを即座に取得。 | **FE**: `frontend/src/features/websocket/hooks/useWebSocket.ts` (`fetchMissingMessages`) |
| **接続時ヒストリー同期** | 接続開始時に「最後に持っているID」を送り、不在時の差分を一括取得。 | **BE**: `backend/src/presentation/websockets/endpoint.py`<br>**FE**: `frontend/src/features/websocket/hooks/useWebSocket.ts` |
| **バックストップ同期** | 新着がなくても30秒ごとに一度 REST API で整合性をチェック。 | **FE**: `frontend/src/features/websocket/hooks/useWebSocket.ts` (`setInterval`) |

---

## 実装の詳細（抜粋）

### シーケンス番号の付与 (Backend)
PostgreSQL の ID はロールバック等で欠番が出る可能性があるため、Redis でアトミックに採番しています。
```python
# backend/src/infrastructure/messaging/redis_publisher.py
seq = await self._redis.incr(settings.REDIS_SEQ_KEY)
await self._redis.publish(channel, json.dumps({**event, "seq": seq}))
```

### ギャップ検知とリカバリ (Frontend)
メッセージハンドラ内で常に `seq` の連続性をチェックしています。
```typescript
// frontend/src/features/websocket/handlers/messageHandlers.ts
if (lastSeq.current !== null && msg.seq !== lastSeq.current + 1) {
  // ギャップ検知！ REST API で補完を指示
  fetchMissingMessages(lastId.current);
}
```

### 指数バックオフ (Frontend)
再試行ごとに待機時間を倍増させ、ネットワーク復帰時にリセットします。
```typescript
// frontend/src/features/websocket/hooks/useWebSocket.ts
const delay = retryMsRef.current;
retryMsRef.current = Math.min(delay * 2, MAX_RETRY_MS); // 最大30秒まで
```
