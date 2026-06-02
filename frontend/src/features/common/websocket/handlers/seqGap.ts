import type { RefObject } from "react";

interface SeqMessage {
  seq?: number | null;
}

export function checkSeqGap<T extends SeqMessage>(
  data: T,
  sequenceName: string,
  lastIdRef: RefObject<number | null>,
  onGap: () => void,
  setSyncStatus: (value: string) => void,
): void {
  if (data.seq == null) return;

  const seq = data.seq;
  if (lastIdRef.current !== null && seq > lastIdRef.current + 1) {
    setSyncStatus(
      `Gap detected in ${sequenceName}! Recovering at ${new Date().toLocaleTimeString()}`,
    );
    onGap();
    // lastIdRef は回復成功後に useFeedSync が更新するため、ここでは進めない
    return;
  }

  if (lastIdRef.current === null || seq > lastIdRef.current) {
    lastIdRef.current = seq;
  }
}
