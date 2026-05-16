import type {
  ErrorMessage,
  GlobalChatMessage,
  RequestMessage,
  RequestUpdateMessage,
  ServerMessage,
} from "@/types/ws";
import { handleGlobalChatMessage } from "./globalChatHandler";
import { handleRequestMessage, handleRequestUpdated } from "./requestHandler";
import { handleError, handlePing, handleSeqGap } from "./systemHandler";
import type { HandlerDeps } from "./types";

export * from "./types";

/**
 * WebSocket の onmessage イベントを処理するメインディスパッチャ。
 * 各メッセージタイプを適切なハンドラに振り分ける。
 */
export function dispatchMessage(
  event: MessageEvent,
  socket: WebSocket,
  deps: HandlerDeps,
): void {
  let data: ServerMessage;
  try {
    data = JSON.parse(event.data);
  } catch (_e) {
    return;
  }

  // ギャップ検知とシーケンスIDの更新
  handleSeqGap(data, deps);

  // 各メッセージタイプに応じた処理
  switch (data.type) {
    case "global_chat":
      handleGlobalChatMessage(data as GlobalChatMessage, deps);
      break;
    case "request":
      handleRequestMessage(data as RequestMessage, deps);
      break;
    case "request_updated":
      handleRequestUpdated(data as RequestUpdateMessage, deps);
      break;
    case "ping":
      handlePing(socket, deps);
      break;
    case "error":
      handleError(data as ErrorMessage, deps);
      break;
    default:
      // 未知のメッセージタイプ
      break;
  }
}
