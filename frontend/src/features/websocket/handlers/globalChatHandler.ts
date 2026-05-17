import { mergeById } from "@/features/websocket/utils/mergeById";
import type { GlobalChatServerMessage } from "@/types/ws";
import type { HandlerDeps } from "./types";

/** グローバルチャットメッセージを受信し、状態を更新する */
export function handleGlobalChatMessage(
  data: GlobalChatServerMessage,
  deps: HandlerDeps,
): void {
  deps.setChatMessages((prev) => {
    if (prev.some((m) => m.id === data.id)) return prev;
    return mergeById(prev, [data]);
  });
}
