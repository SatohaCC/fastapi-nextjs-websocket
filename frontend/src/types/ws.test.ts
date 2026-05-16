import { describe, expect, it } from "vitest";
import {
  isDirectRequestServerMessage,
  isDirectRequestUpdatedServerMessage,
  isGlobalChatServerMessage,
} from "./ws";

describe("WebSocket Type Guards", () => {
  it("should correctly identify GlobalChatServerMessage", () => {
    const mockChat = {
      type: "global_chat",
      id: 1,
      text: "hello",
      username: "alice",
      created_at: "2024-01-01",
      seq: 1,
    } as const;
    const invalidChat = { type: "global_chat", id: 1 };

    expect(isGlobalChatServerMessage(mockChat)).toBe(true);
    expect(isGlobalChatServerMessage(invalidChat)).toBe(false);
    expect(isGlobalChatServerMessage(null)).toBe(false);
  });

  it("should correctly identify DirectRequestServerMessage", () => {
    const mockRequest = {
      type: "direct_request",
      id: 2,
      sender: "alice",
      recipient: "bob",
      text: "help",
      status: "requested",
      created_at: "2024-01-01",
      updated_at: "2024-01-01",
      seq: 2,
    } as const;
    const invalidRequest = { type: "direct_request", sender: "alice" };

    expect(isDirectRequestServerMessage(mockRequest)).toBe(true);
    expect(isDirectRequestServerMessage(invalidRequest)).toBe(false);
  });

  it("should correctly identify DirectRequestUpdatedServerMessage", () => {
    const mockUpdate = {
      type: "direct_request_updated",
      id: 3,
      status: "completed",
      updated_at: "2024-01-01",
      seq: 3,
    } as const;

    expect(isDirectRequestUpdatedServerMessage(mockUpdate)).toBe(true);
    expect(isDirectRequestUpdatedServerMessage({ type: "other" })).toBe(false);
  });
});
