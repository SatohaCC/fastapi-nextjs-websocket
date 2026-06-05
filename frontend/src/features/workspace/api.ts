import type { NotificationSettings } from "@/lib/notificationSettings";

export async function fetchNotificationSettings(): Promise<NotificationSettings> {
  const res = await fetch("/api/proxy/user_settings");
  if (!res.ok) {
    throw new Error("Failed to fetch notification settings");
  }
  const data = await res.json();
  return {
    globalChat: data.global_chat,
    directRequest: data.direct_request,
    directRequestUpdated: data.direct_request_updated,
  };
}

export async function saveNotificationSettings(
  s: NotificationSettings,
): Promise<void> {
  const res = await fetch("/api/proxy/user_settings", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      global_chat: s.globalChat,
      direct_request: s.directRequest,
      direct_request_updated: s.directRequestUpdated,
    }),
  });
  if (!res.ok) {
    throw new Error("Failed to save notification settings");
  }
}
