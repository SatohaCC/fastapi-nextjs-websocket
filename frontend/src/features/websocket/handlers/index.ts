import type {
  DirectRequestMessage,
  DirectRequestUpdateMessage,
  ErrorMessage,
  GlobalChatMessage,
  ServerMessage,
} from "@/types/ws";
import {
  handleDirectRequestMessage,
  handleDirectRequestUpdated,
} from "./directRequestHandler";
import { handleGlobalChatMessage } from "./globalChatHandler";
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
    case "direct_request":
      handleDirectRequestMessage(data as DirectRequestMessage, deps);
      break;
    case "direct_request_updated":
      handleDirectRequestUpdated(data as DirectRequestUpdateMessage, deps);
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
