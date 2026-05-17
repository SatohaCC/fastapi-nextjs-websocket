import { API_BASE } from "@/lib/config";
import type {
  DirectRequestServerMessage,
  DirectRequestUpdatedServerMessage,
} from "@/types/ws";

export async function sendRequest(
  token: string,
  data: { to: string; text: string },
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/direct_requests`, {
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
  taskId: number,
  status: string,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/direct_requests/${taskId}/status`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update status");
}

export type RequestFeedItem =
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
    };

export async function fetchRequestFeeds(
  token: string,
  afterRequestId: number | null,
): Promise<RequestFeedItem[]> {
  try {
    const params = new URLSearchParams();
    params.set("after_request_id", (afterRequestId ?? 0).toString());

    const res = await fetch(
      `${API_BASE}/api/feeds/direct_requests?${params.toString()}`,
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
    console.error("[fetchRequestFeeds] Error:", error);
    throw error;
  }
}
