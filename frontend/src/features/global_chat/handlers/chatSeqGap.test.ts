import { describe, expect, it, vi } from "vitest";
import type { GlobalChatServerMessage } from "@/types/ws";
import { checkChatSeqGap } from "./chatSeqGap";

describe("checkChatSeqGap", () => {
  const makeMessage = (
    overrides: Partial<GlobalChatServerMessage>,
  ): GlobalChatServerMessage => ({
    type: "global_chat",
    username: "alice",
    text: "hello",
    id: 1,
    seq: 1,
    sequence_name: "global_chat",
    created_at: "2026-05-17T00:00:00.000Z",
    ...overrides,
  });

  it("正常なシーケンスの場合、lastChatId を更新し、ギャップ検知は行わない", () => {
    const lastChatId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkChatSeqGap(makeMessage({ seq: 11 }), lastChatId, onGap, setSyncStatus);

    expect(lastChatId.current).toBe(11);
    expect(onGap).not.toHaveBeenCalled();
  });

  it("シーケンスにギャップがある場合、onGap を呼び、setSyncStatus を更新する", () => {
    const lastChatId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkChatSeqGap(makeMessage({ seq: 12 }), lastChatId, onGap, setSyncStatus);

    expect(lastChatId.current).toBe(12);
    expect(onGap).toHaveBeenCalledTimes(1);
    expect(setSyncStatus).toHaveBeenCalledWith(
      expect.stringContaining("Gap detected in global_chat!"),
    );
  });

  it("古いメッセージ (seq が現在より小さい) の場合は何もしない", () => {
    const lastChatId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkChatSeqGap(makeMessage({ seq: 9 }), lastChatId, onGap, setSyncStatus);

    expect(lastChatId.current).toBe(10);
    expect(onGap).not.toHaveBeenCalled();
  });

  it("初回受信 (lastChatId が null) の場合、lastChatId を更新するがギャップ扱いしない", () => {
    const lastChatId = { current: null as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkChatSeqGap(makeMessage({ seq: 5 }), lastChatId, onGap, setSyncStatus);

    expect(lastChatId.current).toBe(5);
    expect(onGap).not.toHaveBeenCalled();
  });

  it("sequence_name が global_chat 以外の場合は何もしない", () => {
    const lastChatId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkChatSeqGap(
      makeMessage({ seq: 11, sequence_name: "direct_request" }),
      lastChatId,
      onGap,
      setSyncStatus,
    );

    expect(lastChatId.current).toBe(10);
    expect(onGap).not.toHaveBeenCalled();
  });

  it("seq が null の場合は何もしない", () => {
    const lastChatId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkChatSeqGap(
      makeMessage({ seq: null }),
      lastChatId,
      onGap,
      setSyncStatus,
    );

    expect(lastChatId.current).toBe(10);
    expect(onGap).not.toHaveBeenCalled();
  });
});
