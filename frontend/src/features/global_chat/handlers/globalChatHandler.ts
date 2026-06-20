import type { Dispatch, SetStateAction } from "react";
import { mergeById } from "@/features/common/websocket/utils/mergeById";
import type { GlobalChatServerMessage } from "@/types/ws";

export function handleGlobalChatMessage(
  data: GlobalChatServerMessage,
  setChatMessages: Dispatch<SetStateAction<GlobalChatServerMessage[]>>,
): void {
  setChatMessages((prev) => {
    if (prev.some((m) => m.id === data.id)) return prev;
    return mergeById(prev, [data]);
  });
}
