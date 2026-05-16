import { describe, expect, it } from "vitest";
import {
  isGlobalChatMessage,
  isRequestMessage,
  isRequestUpdateMessage,
} from "./ws";

describe("WebSocket Type Guards", () => {
  it("should correctly identify GlobalChatMessage", () => {
    const mockChat = {
      type: "global_chat",
      id: 1,
      text: "hello",
      username: "alice",
      created_at: "2024-01-01",
      seq: 1,
    } as const;
    const invalidChat = { type: "global_chat", id: 1 };

    expect(isGlobalChatMessage(mockChat)).toBe(true);
    expect(isGlobalChatMessage(invalidChat)).toBe(false);
    expect(isGlobalChatMessage(null)).toBe(false);
  });

  it("should correctly identify RequestMessage", () => {
    const mockRequest = {
      type: "request",
      id: 2,
      sender: "alice",
      recipient: "bob",
      text: "help",
      status: "requested",
      created_at: "2024-01-01",
      updated_at: "2024-01-01",
      seq: 2,
    } as const;
    const invalidRequest = { type: "request", sender: "alice" };

    expect(isRequestMessage(mockRequest)).toBe(true);
    expect(isRequestMessage(invalidRequest)).toBe(false);
  });

  it("should correctly identify RequestUpdateMessage", () => {
    const mockUpdate = {
      type: "request_updated",
      id: 3,
      status: "completed",
      updated_at: "2024-01-01",
      seq: 3,
    } as const;

    expect(isRequestUpdateMessage(mockUpdate)).toBe(true);
    expect(isRequestUpdateMessage({ type: "other" })).toBe(false);
  });
});
