// Server -> Client Messages
export type ServerMessage =
  | GlobalChatMessage
  | DirectRequestMessage
  | DirectRequestUpdateMessage
  | JoinLeaveMessage
  | PingMessage
  | ErrorMessage;

export interface GlobalChatMessage {
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

export interface DirectRequestMessage {
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

export interface DirectRequestUpdateMessage {
  type: "direct_request_updated";
  id: number;
  seq: number | null; // delivery_feeds.id (欠番なし連番)
  sequence_name?: string;
  status: TaskStatus;
  sender: string;
  recipient: string;
  updated_at: string;
}

export interface JoinLeaveMessage {
  type: "join" | "leave";
  username: string;
}

export interface PingMessage {
  type: "ping";
}

export interface ErrorMessage {
  type: "error";
  text: string;
}

// Client -> Server Messages
export type ClientMessage =
  | GlobalChatOut
  | DirectRequestOut
  | UpdateDirectRequestStatusOut
  | PongOut;

export interface GlobalChatOut {
  type: "global_chat";
  text: string;
}

export interface DirectRequestOut {
  type: "direct_request";
  to: string;
  text: string;
}

export interface UpdateDirectRequestStatusOut {
  type: "update_status";
  task_id: number;
  status: TaskStatus;
}

export interface PongOut {
  type: "pong";
}

// Type Guards
export function isGlobalChatMessage(data: unknown): data is GlobalChatMessage {
  if (typeof data !== "object" || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    d.type === "global_chat" &&
    typeof d.id === "number" &&
    typeof d.text === "string"
  );
}

export function isDirectRequestMessage(
  data: unknown,
): data is DirectRequestMessage {
  if (typeof data !== "object" || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    d.type === "direct_request" &&
    typeof d.id === "number" &&
    typeof d.sender === "string"
  );
}

export function isDirectRequestUpdateMessage(
  data: unknown,
): data is DirectRequestUpdateMessage {
  if (typeof data !== "object" || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    d.type === "direct_request_updated" &&
    typeof d.id === "number" &&
    typeof d.status === "string"
  );
}
