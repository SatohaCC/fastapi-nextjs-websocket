import { API_BASE } from "@/lib/config";
import type { ChatMessage } from "@/types/ws";

export async function fetchMessages(
  token: string,
  afterId: number,
): Promise<ChatMessage[]> {
  const res = await fetch(`${API_BASE}/api/messages?after_id=${afterId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch messages");
  return res.json();
}
