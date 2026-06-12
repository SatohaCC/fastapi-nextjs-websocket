import { describe, expect, it } from "vitest";
import type { GlobalChatServerMessage } from "@/types/ws";
import { handleGlobalChatMessage } from "./globalChatHandler";

// 初期接続のオーバーラップ（スナップショット履歴 + ライブ）は id で重複排除される、
// という不変条件を固定するテスト。これが崩れると重複表示やギャップの穴になる。

const make = (
  overrides: Partial<GlobalChatServerMessage>,
): GlobalChatServerMessage => ({
  type: "global_chat",
  username: "alice",
  text: "hello",
  id: 1,
  seq: null,
  created_at: "2026-05-17T00:00:00.000Z",
  is_history: false,
  ...overrides,
});

/** setState ディスパッチャを模し、updater を現在状態に適用するヘルパー。 */
function applyHandler(
  initial: GlobalChatServerMessage[],
  msg: GlobalChatServerMessage,
): GlobalChatServerMessage[] {
  let state = initial;
  handleGlobalChatMessage(msg, (updater) => {
    state =
      typeof updater === "function"
        ? (
            updater as (
              p: GlobalChatServerMessage[],
            ) => GlobalChatServerMessage[]
          )(state)
        : updater;
  });
  return state;
}

describe("handleGlobalChatMessage", () => {
  it("新しい id は追加する", () => {
    const next = applyHandler(
      [make({ id: 1 })],
      make({ id: 2, text: "world" }),
    );
    expect(next.map((m) => m.id)).toEqual([1, 2]);
  });

  it("同じ id は重複追加しない（オーバーラップの dedup）", () => {
    const live = make({ id: 5, text: "live", seq: 5, is_history: false });
    const history = make({ id: 5, text: "live", seq: 5, is_history: true });
    // 履歴 → ライブ、ライブ → 履歴 のどちらの順でも 1 件に収束する。
    const a = applyHandler([history], live);
    const b = applyHandler([live], history);
    expect(a).toHaveLength(1);
    expect(b).toHaveLength(1);
  });

  it("同じ id のとき既存エントリを保持する（参照を変えない）", () => {
    const prev = [make({ id: 7, text: "first" })];
    const next = applyHandler(prev, make({ id: 7, text: "second" }));
    expect(next).toBe(prev);
  });
});
