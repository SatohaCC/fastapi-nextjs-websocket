import { API_BASE } from "@/lib/config";
import type { DirectRequestServerMessage } from "@/types/ws";

export async function fetchRequests(
  token: string,
  afterId: number,
): Promise<DirectRequestServerMessage[]> {
  const res = await fetch(
    `${API_BASE}/api/direct_requests?after_id=${afterId}`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  );
  if (!res.ok) throw new Error("Failed to fetch requests");
  return res.json();
}
