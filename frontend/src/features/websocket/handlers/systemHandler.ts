import type { RefObject } from "react";
import type { ServerMessage } from "@/types/ws";
import type { HandlerDeps } from "./types";

/** シーケンスギャップを検出し、不足データを補完する */
export function handleSeqGap(data: ServerMessage, deps: HandlerDeps): void {
  if (
    !("seq" in data) ||
    data.seq == null ||
    !("sequence_name" in data) ||
    data.sequence_name == null
  )
    return;

  const seqName = data.sequence_name as string;
  const seq = data.seq;

  let lastIdRef: RefObject<number | null> | null = null;

  if (seqName === "global_chat") {
    lastIdRef = deps.lastChatId;
  } else if (seqName === "direct_request") {
    lastIdRef = deps.lastRequestId;
  }

  if (lastIdRef) {
    if (lastIdRef.current !== null && seq > lastIdRef.current + 1) {
      deps.setSyncStatus(
        `Gap detected in ${seqName}! Recovering at ${new Date().toLocaleTimeString()}`,
      );
      deps.fetchMissingFeeds();
    }

    if (lastIdRef.current === null || seq > lastIdRef.current) {
      lastIdRef.current = seq;
    }
  }
}

/** Ping メッセージに応答する */
export function handlePing(socket: WebSocket, deps: HandlerDeps): void {
  socket.send(JSON.stringify({ type: "pong" }));
  deps.resetPingTimeout(socket);
  deps.setHeartbeatStatus(`Heartbeat: ${new Date().toLocaleTimeString()}`);
}

/** エラーメッセージを処理する */
export function handleError(data: { text: string }, deps: HandlerDeps): void {
  deps.setError(data.text);
  deps.setSyncStatus("Connection error");
}
