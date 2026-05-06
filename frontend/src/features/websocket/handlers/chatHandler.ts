import { mergeById } from "@/features/websocket/utils/mergeById";
import type { ChatMessage } from "@/types/ws";
import type { HandlerDeps } from "./types";

/** チャットメッセージを受信し、状態を更新する */
export function handleChatMessage(data: ChatMessage, deps: HandlerDeps): void {
  deps.setChatMessages((prev) => {
    if (prev.some((m) => m.id === data.id)) return prev;
    return mergeById(prev, [data]);
  });
}
