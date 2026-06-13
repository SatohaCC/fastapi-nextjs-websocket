import { apiClient } from "@/lib/apiClient";
import type { GlobalChatServerMessage } from "@/types/ws";

export async function sendMessage(text: string): Promise<void> {
  const res = await apiClient("/api/proxy/global_chat/messages", {
    method: "POST",
    headers: {
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
  afterChatId: number | null,
): Promise<ChatFeedItem[]> {
  try {
    const params = new URLSearchParams();
    params.set("after_chat_id", (afterChatId ?? 0).toString());

    const res = await apiClient(
      `/api/proxy/feeds/global_chat?${params.toString()}`,
    );
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(
        `${errorData.detail || "Error"} (${res.status}) at ${res.url}`,
      );
    }
    return res.json();
  } catch (error) {
    if (error instanceof Error && error.name === "UnauthorizedError") {
      throw error;
    }
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[fetchChatFeeds] Error:", error);
    throw error;
  }
}
