import { apiClient } from "@/lib/apiClient";
import type {
  DirectRequestServerMessage,
  DirectRequestUpdatedServerMessage,
} from "@/types/ws";

export async function sendRequest(data: {
  to: string;
  text: string;
}): Promise<void> {
  const res = await apiClient("/api/proxy/direct_requests", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to send request");
}

export async function updateRequestStatus(
  taskId: number,
  status: string,
): Promise<void> {
  const res = await apiClient(`/api/proxy/direct_requests/${taskId}/status`, {
    method: "PATCH",
    headers: {
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
  afterRequestId: number | null,
): Promise<RequestFeedItem[]> {
  try {
    const params = new URLSearchParams();
    params.set("after_request_id", (afterRequestId ?? 0).toString());

    const res = await apiClient(
      `/api/proxy/feeds/direct_requests?${params.toString()}`,
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
