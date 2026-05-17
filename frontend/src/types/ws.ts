// 命名規則 (../../../CONVENTIONS.md 第 1 節):
//   - *ServerMessage: サーバー → クライアント (受信)
//   - *ClientMessage: クライアント → サーバー (送信)

// --- Server -> Client Messages ---
export type ServerMessage =
  | GlobalChatServerMessage
  | DirectRequestServerMessage
  | DirectRequestUpdatedServerMessage
  | JoinLeaveServerMessage
  | PingServerMessage
  | ErrorServerMessage;

export interface GlobalChatServerMessage {
  type: "global_chat";
  username: string;
  text: string;
  id: number;
  seq: number | null; // delivery_feeds.id (欠番なし連番)
  sequence_name?: string;
  created_at: string;
  is_history?: boolean;
}

export type TaskStatus = "requested" | "processing" | "completed";

export interface DirectRequestServerMessage {
  type: "direct_request";
  id: number;
  seq: number | null; // delivery_feeds.id (欠番なし連番)
  sequence_name?: string;
  sender: string;
  recipient: string;
  text: string;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
  is_history?: boolean;
}

export interface DirectRequestUpdatedServerMessage {
  type: "direct_request_updated";
  id: number;
  seq: number | null; // delivery_feeds.id (欠番なし連番)
  sequence_name?: string;
  status: TaskStatus;
  sender: string;
  recipient: string;
  updated_at: string;
}

export interface JoinLeaveServerMessage {
  type: "join" | "leave";
  username: string;
}

export interface PingServerMessage {
  type: "ping";
}

export interface ErrorServerMessage {
  type: "error";
  text: string;
}

// --- Client -> Server Messages ---
export type ClientMessage =
  | GlobalChatClientMessage
  | DirectRequestClientMessage
  | UpdateDirectRequestStatusClientMessage
  | PongClientMessage;

export interface GlobalChatClientMessage {
  type: "global_chat";
  text: string;
}

export interface DirectRequestClientMessage {
  type: "direct_request";
  to: string;
  text: string;
}

export interface UpdateDirectRequestStatusClientMessage {
  type: "update_status";
  task_id: number;
  status: TaskStatus;
}

export interface PongClientMessage {
  type: "pong";
}

// --- Type Guards ---
export function isGlobalChatServerMessage(
  data: unknown,
): data is GlobalChatServerMessage {
  if (typeof data !== "object" || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    d.type === "global_chat" &&
    typeof d.id === "number" &&
    typeof d.text === "string"
  );
}

export function isDirectRequestServerMessage(
  data: unknown,
): data is DirectRequestServerMessage {
  if (typeof data !== "object" || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    d.type === "direct_request" &&
    typeof d.id === "number" &&
    typeof d.sender === "string"
  );
}

export function isDirectRequestUpdatedServerMessage(
  data: unknown,
): data is DirectRequestUpdatedServerMessage {
  if (typeof data !== "object" || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    d.type === "direct_request_updated" &&
    typeof d.id === "number" &&
    typeof d.status === "string"
  );
}
