import { describe, expect, it, vi } from "vitest";
import type {
  DirectRequestServerMessage,
  GlobalChatServerMessage,
} from "@/types/ws";
import { checkSeqGap } from "./seqGap";

// Note: sequence_name はバックエンドから送信されないため checkSeqGap は seq のみで判定する。
// メッセージの種類フィルタリングは useWsSubscribe のチャンネル購読が保証する。

describe("checkSeqGap", () => {
  describe("global_chat シーケンス", () => {
    const makeMessage = (
      overrides: Partial<GlobalChatServerMessage>,
    ): GlobalChatServerMessage => ({
      type: "global_chat",
      username: "alice",
      text: "hello",
      id: 1,
      seq: 1,
      created_at: "2026-05-17T00:00:00.000Z",
      ...overrides,
      is_history: overrides.is_history ?? false,
    });

    it("正常なシーケンスの場合、lastId を更新し、ギャップ検知は行わない", () => {
      const lastId = { current: 10 as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: 11 }),
        "global_chat",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(11);
      expect(onGap).not.toHaveBeenCalled();
    });

    it("シーケンスにギャップがある場合、onGap を呼び、lastId は進めない", () => {
      const lastId = { current: 10 as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: 12 }),
        "global_chat",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(10);
      expect(onGap).toHaveBeenCalledTimes(1);
      expect(setSyncStatus).toHaveBeenCalledWith(
        expect.stringContaining("Gap detected in global_chat!"),
      );
    });

    it("古いメッセージ (seq が現在より小さい) の場合は何もしない", () => {
      const lastId = { current: 10 as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: 9 }),
        "global_chat",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(10);
      expect(onGap).not.toHaveBeenCalled();
    });

    it("初回受信 (lastId が null) の場合、lastId を更新するがギャップ扱いしない", () => {
      const lastId = { current: null as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: 5 }),
        "global_chat",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(5);
      expect(onGap).not.toHaveBeenCalled();
    });

    it("seq が null の場合は何もしない", () => {
      const lastId = { current: 10 as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: null }),
        "global_chat",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(10);
      expect(onGap).not.toHaveBeenCalled();
    });
  });

  describe("direct_request シーケンス", () => {
    const makeMessage = (
      overrides: Partial<DirectRequestServerMessage>,
    ): DirectRequestServerMessage => ({
      type: "direct_request",
      id: 1,
      seq: 1,
      sender: "alice",
      recipient: "bob",
      text: "do it",
      status: "requested",
      created_at: "2026-05-17T00:00:00.000Z",
      updated_at: "2026-05-17T00:00:00.000Z",
      ...overrides,
      is_history: overrides.is_history ?? false,
    });

    it("正常なシーケンスの場合、lastId を更新し、ギャップ検知は行わない", () => {
      const lastId = { current: 10 as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: 11 }),
        "direct_request",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(11);
      expect(onGap).not.toHaveBeenCalled();
    });

    it("シーケンスにギャップがある場合、onGap を呼び、lastId は進めない", () => {
      const lastId = { current: 10 as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: 12 }),
        "direct_request",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(10);
      expect(onGap).toHaveBeenCalledTimes(1);
      expect(setSyncStatus).toHaveBeenCalledWith(
        expect.stringContaining("Gap detected in direct_request!"),
      );
    });

    it("古いメッセージ (seq が現在より小さい) の場合は何もしない", () => {
      const lastId = { current: 10 as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: 9 }),
        "direct_request",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(10);
      expect(onGap).not.toHaveBeenCalled();
    });

    it("初回受信 (lastId が null) の場合、lastId を更新するがギャップ扱いしない", () => {
      const lastId = { current: null as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: 5 }),
        "direct_request",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(5);
      expect(onGap).not.toHaveBeenCalled();
    });

    it("seq が null の場合は何もしない", () => {
      const lastId = { current: 10 as number | null };
      const onGap = vi.fn();
      const setSyncStatus = vi.fn();

      checkSeqGap(
        makeMessage({ seq: null }),
        "direct_request",
        lastId,
        onGap,
        setSyncStatus,
      );

      expect(lastId.current).toBe(10);
      expect(onGap).not.toHaveBeenCalled();
    });
  });
});
