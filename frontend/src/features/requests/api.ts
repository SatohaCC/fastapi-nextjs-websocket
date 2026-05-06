import { API_BASE } from "@/lib/config";
import type { RequestMessage } from "@/types/ws";

export async function fetchRequests(
  token: string,
  afterId: number,
): Promise<RequestMessage[]> {
  const res = await fetch(`${API_BASE}/api/requests?after_id=${afterId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch requests");
  return res.json();
}
