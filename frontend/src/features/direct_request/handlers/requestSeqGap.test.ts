import { describe, expect, it, vi } from "vitest";
import type { DirectRequestServerMessage } from "@/types/ws";
import { checkRequestSeqGap } from "./requestSeqGap";

describe("checkRequestSeqGap", () => {
  const makeMessage = (
    overrides: Partial<DirectRequestServerMessage>,
  ): DirectRequestServerMessage => ({
    type: "direct_request",
    id: 1,
    seq: 1,
    sequence_name: "direct_request",
    sender: "alice",
    recipient: "bob",
    text: "do it",
    status: "requested",
    created_at: "2026-05-17T00:00:00.000Z",
    updated_at: "2026-05-17T00:00:00.000Z",
    ...overrides,
  });

  it("正常なシーケンスの場合、lastRequestId を更新し、ギャップ検知は行わない", () => {
    const lastRequestId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkRequestSeqGap(
      makeMessage({ seq: 11 }),
      lastRequestId,
      onGap,
      setSyncStatus,
    );

    expect(lastRequestId.current).toBe(11);
    expect(onGap).not.toHaveBeenCalled();
  });

  it("シーケンスにギャップがある場合、onGap を呼び、setSyncStatus を更新する", () => {
    const lastRequestId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkRequestSeqGap(
      makeMessage({ seq: 12 }),
      lastRequestId,
      onGap,
      setSyncStatus,
    );

    expect(lastRequestId.current).toBe(12);
    expect(onGap).toHaveBeenCalledTimes(1);
    expect(setSyncStatus).toHaveBeenCalledWith(
      expect.stringContaining("Gap detected in direct_request!"),
    );
  });

  it("古いメッセージ (seq が現在より小さい) の場合は何もしない", () => {
    const lastRequestId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkRequestSeqGap(
      makeMessage({ seq: 9 }),
      lastRequestId,
      onGap,
      setSyncStatus,
    );

    expect(lastRequestId.current).toBe(10);
    expect(onGap).not.toHaveBeenCalled();
  });

  it("初回受信 (lastRequestId が null) の場合、lastRequestId を更新するがギャップ扱いしない", () => {
    const lastRequestId = { current: null as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkRequestSeqGap(
      makeMessage({ seq: 5 }),
      lastRequestId,
      onGap,
      setSyncStatus,
    );

    expect(lastRequestId.current).toBe(5);
    expect(onGap).not.toHaveBeenCalled();
  });

  it("sequence_name が direct_request 以外の場合は何もしない", () => {
    const lastRequestId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkRequestSeqGap(
      makeMessage({ seq: 11, sequence_name: "global_chat" }),
      lastRequestId,
      onGap,
      setSyncStatus,
    );

    expect(lastRequestId.current).toBe(10);
    expect(onGap).not.toHaveBeenCalled();
  });

  it("seq が null の場合は何もしない", () => {
    const lastRequestId = { current: 10 as number | null };
    const onGap = vi.fn();
    const setSyncStatus = vi.fn();

    checkRequestSeqGap(
      makeMessage({ seq: null }),
      lastRequestId,
      onGap,
      setSyncStatus,
    );

    expect(lastRequestId.current).toBe(10);
    expect(onGap).not.toHaveBeenCalled();
  });
});
