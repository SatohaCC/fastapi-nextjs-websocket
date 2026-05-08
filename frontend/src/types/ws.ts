// Server -> Client Messages
export type ServerMessage =
  | ChatMessage
  | RequestMessage
  | RequestUpdateMessage
  | JoinLeaveMessage
  | PingMessage
  | ErrorMessage;

export interface ChatMessage {
  type: "message";
  username: string;
  text: string;
  id: number;
  seq: number | null; // delivery_feeds.id (欠番なし連番)
  sequence_name?: string;
  created_at: string;
  is_history?: boolean;
}

export type RequestStatus = "requested" | "processing" | "completed";

export interface RequestMessage {
  type: "request";
  id: number;
  seq: number | null; // delivery_feeds.id (欠番なし連番)
  sequence_name?: string;
  sender: string;
  recipient: string;
  text: string;
  status: RequestStatus;
  created_at: string;
  updated_at: string;
  is_history?: boolean;
}

export interface RequestUpdateMessage {
  type: "request_updated";
  id: number;
  seq: number | null; // delivery_feeds.id (欠番なし連番)
  sequence_name?: string;
  status: RequestStatus;
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
export type ClientMessage = ChatOut | RequestOut | UpdateStatusOut | PongOut;

export interface ChatOut {
  type: "message";
  text: string;
}

export interface RequestOut {
  type: "request";
  to: string;
  text: string;
}

export interface UpdateStatusOut {
  type: "update_status";
  request_id: number;
  status: RequestStatus;
}

export interface PongOut {
  type: "pong";
}

// Type Guards
export function isChatMessage(data: unknown): data is ChatMessage {
  if (typeof data !== "object" || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    d.type === "message" &&
    typeof d.id === "number" &&
    typeof d.text === "string"
  );
}

export function isRequestMessage(data: unknown): data is RequestMessage {
  if (typeof data !== "object" || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    d.type === "request" &&
    typeof d.id === "number" &&
    typeof d.sender === "string"
  );
}

export function isRequestUpdateMessage(
  data: unknown,
): data is RequestUpdateMessage {
  if (typeof data !== "object" || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    d.type === "request_updated" &&
    typeof d.id === "number" &&
    typeof d.status === "string"
  );
}
