import { API_BASE } from "@/lib/config";

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
