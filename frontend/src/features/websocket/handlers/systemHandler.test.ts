import { describe, expect, it, vi } from "vitest";
import type { ServerMessage } from "@/types/ws";
import { handleSeqGap } from "./systemHandler";
import type { HandlerDeps } from "./types";

describe("handleSeqGap", () => {
  const createMockDeps = (overrides = {}): HandlerDeps => ({
    lastChatId: { current: null },
    lastRequestId: { current: null },
    setChatMessages: vi.fn(),
    setRequestMessages: vi.fn(),
    setSyncStatus: vi.fn(),
    setError: vi.fn(),
    fetchMissingFeeds: vi.fn(),
    resetPingTimeout: vi.fn(),
    setHeartbeatStatus: vi.fn(),
    ...overrides,
  });

  it("正常なシーケンスの場合、lastId を更新し、ギャップ検知は行わない", () => {
    const deps = createMockDeps({ lastChatId: { current: 10 } });
    const message = { type: "message", sequence_name: "chat_global", seq: 11 };

    handleSeqGap(message as unknown as ServerMessage, deps);

    expect(deps.lastChatId.current).toBe(11);
    expect(deps.fetchMissingFeeds).not.toHaveBeenCalled();
  });

  it("シーケンスにギャップがある場合、fetchMissingFeeds を呼び出し、ステータスを更新する", () => {
    const deps = createMockDeps({ lastChatId: { current: 10 } });
    const message = { type: "message", sequence_name: "chat_global", seq: 12 };

    handleSeqGap(message as unknown as ServerMessage, deps);

    expect(deps.lastChatId.current).toBe(12);
    expect(deps.fetchMissingFeeds).toHaveBeenCalled();
    expect(deps.setSyncStatus).toHaveBeenCalledWith(
      expect.stringContaining("Gap detected in chat_global!"),
    );
  });

  it("古いメッセージ（seq が現在より小さい）の場合、何もしない", () => {
    const deps = createMockDeps({ lastChatId: { current: 10 } });
    const message = { type: "message", sequence_name: "chat_global", seq: 9 };

    handleSeqGap(message as unknown as ServerMessage, deps);

    expect(deps.lastChatId.current).toBe(10);
    expect(deps.fetchMissingFeeds).not.toHaveBeenCalled();
  });

  it("初回受信（lastId が null）の場合、lastId を更新する", () => {
    const deps = createMockDeps({ lastChatId: { current: null } });
    const message = { type: "message", sequence_name: "chat_global", seq: 5 };

    handleSeqGap(message as unknown as ServerMessage, deps);

    expect(deps.lastChatId.current).toBe(5);
    expect(deps.fetchMissingFeeds).not.toHaveBeenCalled();
  });

  it("対象外のシーケンス名の場合は何もしない", () => {
    const deps = createMockDeps({ lastChatId: { current: 10 } });
    const message = { type: "message", sequence_name: "unknown_seq", seq: 11 };

    handleSeqGap(message as unknown as ServerMessage, deps);

    expect(deps.lastChatId.current).toBe(10);
  });

  it("seq が null の場合は何もしない", () => {
    const deps = createMockDeps({ lastChatId: { current: 10 } });
    const message = {
      type: "message",
      sequence_name: "chat_global",
      seq: null,
    };

    handleSeqGap(message as unknown as ServerMessage, deps);

    expect(deps.lastChatId.current).toBe(10);
    expect(deps.fetchMissingFeeds).not.toHaveBeenCalled();
  });

  it("sequence_name がない場合は何もしない", () => {
    const deps = createMockDeps({ lastChatId: { current: 10 } });
    const message = { type: "ping" };

    handleSeqGap(message as unknown as ServerMessage, deps);

    expect(deps.lastChatId.current).toBe(10);
    expect(deps.fetchMissingFeeds).not.toHaveBeenCalled();
  });
});
