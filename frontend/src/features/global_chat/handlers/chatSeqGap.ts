import type { RefObject } from "react";
import type { GlobalChatServerMessage } from "@/types/ws";

export function checkChatSeqGap(
  data: GlobalChatServerMessage,
  lastChatIdRef: RefObject<number | null>,
  onGap: () => void,
  setSyncStatus: (value: string) => void,
): void {
  if (data.seq == null || data.sequence_name !== "global_chat") return;

  const seq = data.seq;
  if (lastChatIdRef.current !== null && seq > lastChatIdRef.current + 1) {
    setSyncStatus(
      `Gap detected in global_chat! Recovering at ${new Date().toLocaleTimeString()}`,
    );
    onGap();
  }

  if (lastChatIdRef.current === null || seq > lastChatIdRef.current) {
    lastChatIdRef.current = seq;
  }
}
