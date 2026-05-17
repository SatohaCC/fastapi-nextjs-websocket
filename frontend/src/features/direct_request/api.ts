import { API_BASE } from "@/lib/config";

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
