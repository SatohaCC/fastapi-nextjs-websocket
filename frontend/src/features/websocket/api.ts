import { API_BASE } from "@/lib/config";

export interface FeedResponse {
  sequence_name: string;
  sequence_id: number;
  event_type: "message" | "request" | "request_updated";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  payload: any;
  created_at: string;
}

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

export async function sendMessage(token: string, text: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/messages`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("Failed to send message");
}

export async function sendRequest(
  token: string,
  data: { to: string; text: string },
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/requests`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to send request");
}

export async function updateRequestStatus(
  token: string,
  requestId: number,
  status: string,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/requests/${requestId}/status`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update status");
}
