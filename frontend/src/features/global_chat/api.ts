import { API_BASE } from "@/lib/config";
import type { GlobalChatServerMessage } from "@/types/ws";

export async function sendMessage(token: string, text: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/global_chat/messages`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("Failed to send message");
}

export interface ChatFeedItem {
  event_type: "global_chat";
  payload: GlobalChatServerMessage;
  sequence_name: string;
  sequence_id: number;
  created_at: string;
}

export async function fetchChatFeeds(
  token: string,
  afterChatId: number | null,
): Promise<ChatFeedItem[]> {
  try {
    const params = new URLSearchParams();
    params.set("after_chat_id", (afterChatId ?? 0).toString());

    const res = await fetch(
      `${API_BASE}/api/feeds/global_chat?${params.toString()}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(
        `${errorData.detail || "Error"} (${res.status}) at ${res.url}`,
      );
    }
    return res.json();
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[fetchChatFeeds] Error:", error);
    throw error;
  }
}
