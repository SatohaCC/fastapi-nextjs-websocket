import { API_BASE } from "@/lib/config";
import type {
  DirectRequestServerMessage,
  DirectRequestUpdatedServerMessage,
  GlobalChatServerMessage,
  JoinLeaveServerMessage,
} from "@/types/ws";

export type FeedResponse =
  | {
      event_type: "global_chat";
      payload: GlobalChatServerMessage;
      sequence_name: string;
      sequence_id: number;
      created_at: string;
    }
  | {
      event_type: "direct_request";
      payload: DirectRequestServerMessage;
      sequence_name: string;
      sequence_id: number;
      created_at: string;
    }
  | {
      event_type: "direct_request_updated";
      payload: DirectRequestUpdatedServerMessage;
      sequence_name: string;
      sequence_id: number;
      created_at: string;
    }
  | {
      event_type: "join" | "leave";
      payload: JoinLeaveServerMessage;
      sequence_name: string;
      sequence_id: number;
      created_at: string;
    };

export async function fetchFeeds(
  token: string,
  afterChatId?: number | null,
  afterRequestId?: number | null,
): Promise<FeedResponse[]> {
  try {
    const params = new URLSearchParams();
    if (afterChatId != null)
      params.set("after_chat_id", afterChatId.toString());
    if (afterRequestId != null)
      params.set("after_request_id", afterRequestId.toString());

    const res = await fetch(`${API_BASE}/api/feeds?${params.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(
        `${errorData.detail || "Error"} (${res.status}) at ${res.url}`,
      );
    }
    return res.json();
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[fetchFeeds] Error:", error);
    throw error;
  }
}
