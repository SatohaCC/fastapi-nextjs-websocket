import type { RefObject } from "react";
import type {
  DirectRequestServerMessage,
  DirectRequestUpdatedServerMessage,
} from "@/types/ws";

export function checkRequestSeqGap(
  data: DirectRequestServerMessage | DirectRequestUpdatedServerMessage,
  lastRequestIdRef: RefObject<number | null>,
  onGap: () => void,
  setSyncStatus: (value: string) => void,
): void {
  if (data.seq == null || data.sequence_name !== "direct_request") return;

  const seq = data.seq;
  if (lastRequestIdRef.current !== null && seq > lastRequestIdRef.current + 1) {
    setSyncStatus(
      `Gap detected in direct_request! Recovering at ${new Date().toLocaleTimeString()}`,
    );
    onGap();
  }

  if (lastRequestIdRef.current === null || seq > lastRequestIdRef.current) {
    lastRequestIdRef.current = seq;
  }
}
