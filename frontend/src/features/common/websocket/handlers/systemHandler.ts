export interface SystemHandlerCtx {
  resetPingTimeout: (socket: WebSocket) => void;
  setHeartbeatStatus: (value: string) => void;
  setError: (value: string | null) => void;
  setSyncStatus: (value: string) => void;
}

export function handlePing(socket: WebSocket, ctx: SystemHandlerCtx): void {
  socket.send(JSON.stringify({ type: "pong" }));
  ctx.resetPingTimeout(socket);
  ctx.setHeartbeatStatus(`Heartbeat: ${new Date().toLocaleTimeString()}`);
}

export function handleError(
  data: { text: string },
  ctx: SystemHandlerCtx,
): void {
  ctx.setError(data.text);
  ctx.setSyncStatus("Connection error");
}
