import type { WsHandler } from "../context/WebSocketContext";
import {
  handleError,
  handlePing,
  type SystemHandlerCtx,
} from "./systemHandler";

interface DispatchCtx extends SystemHandlerCtx {
  subscribers: Map<string, Set<WsHandler>>;
}

/**
 * WebSocket の onmessage を JSON パースし、type ごとに購読者へ配信する。
 * `ping` / `error` は購読者を介さず内部の systemHandler に直送する。
 */
export function dispatch(
  event: MessageEvent,
  socket: WebSocket,
  ctx: DispatchCtx,
): void {
  let data: { type?: unknown; [key: string]: unknown };
  try {
    data = JSON.parse(event.data);
  } catch {
    return;
  }
  if (!data || typeof data.type !== "string") return;

  if (data.type === "ping") {
    handlePing(socket, ctx);
    return;
  }
  if (data.type === "error" && typeof data.text === "string") {
    handleError(data as { text: string }, ctx);
    return;
  }

  const set = ctx.subscribers.get(data.type);
  if (!set) return;
  for (const handler of set) {
    handler(data, socket);
  }
}
