import { describe, expect, it } from "vitest";
import { applyPresence, toSortedUsernames } from "./presenceReducer";

describe("applyPresence", () => {
  it("presence_state はロスター全体を置き換える", () => {
    const start = new Set(["old"]);
    const next = applyPresence(start, {
      type: "presence_state",
      usernames: ["alice", "bob"],
    });
    expect([...next].sort()).toEqual(["alice", "bob"]);
  });

  it("join は追加する", () => {
    const next = applyPresence(new Set(["alice"]), {
      type: "join",
      username: "bob",
    });
    expect(next.has("bob")).toBe(true);
    expect(next.has("alice")).toBe(true);
  });

  it("leave は削除する", () => {
    const next = applyPresence(new Set(["alice", "bob"]), {
      type: "leave",
      username: "bob",
    });
    expect(next.has("bob")).toBe(false);
    expect(next.has("alice")).toBe(true);
  });

  it("join は冪等（重複追加で同一参照を返す）", () => {
    const start = new Set(["alice"]);
    const next = applyPresence(start, { type: "join", username: "alice" });
    expect(next).toBe(start);
  });

  it("leave は存在しないユーザーに対して同一参照を返す", () => {
    const start = new Set(["alice"]);
    const next = applyPresence(start, { type: "leave", username: "ghost" });
    expect(next).toBe(start);
  });

  it("元の集合を変更しない（イミュータブル）", () => {
    const start = new Set(["alice"]);
    applyPresence(start, { type: "join", username: "bob" });
    applyPresence(start, { type: "leave", username: "alice" });
    expect([...start]).toEqual(["alice"]);
  });

  it("スナップショット後の差分が順番に反映される", () => {
    let state = applyPresence(new Set<string>(), {
      type: "presence_state",
      usernames: ["alice", "bob"],
    });
    state = applyPresence(state, { type: "join", username: "charlie" });
    state = applyPresence(state, { type: "leave", username: "alice" });
    expect(toSortedUsernames(state)).toEqual(["bob", "charlie"]);
  });
});

describe("toSortedUsernames", () => {
  it("ソート済み配列を返す", () => {
    expect(toSortedUsernames(new Set(["charlie", "alice", "bob"]))).toEqual([
      "alice",
      "bob",
      "charlie",
    ]);
  });

  it("空集合は空配列", () => {
    expect(toSortedUsernames(new Set())).toEqual([]);
  });
});
