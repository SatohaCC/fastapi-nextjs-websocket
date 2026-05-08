import { afterEach, beforeAll } from "vitest";
import { WebSocketMock } from "./mocks/WebSocketMock";
import { worker } from "./msw/browser";

beforeAll(() => {
  Object.defineProperty(globalThis, "WebSocket", {
    value: WebSocketMock,
    writable: true,
    configurable: true,
  });
});

afterEach(() => {
  worker.resetHandlers();
  WebSocketMock.clearInstances();
});
