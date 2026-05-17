import { HttpResponse, http } from "msw";
import { API_BASE } from "@/lib/config";

export const handlers = [
  http.post(`${API_BASE}/api/auth/token`, () => {
    return HttpResponse.json({ access_token: "mock-token" });
  }),

  http.get(`${API_BASE}/api/auth/users`, () => {
    return HttpResponse.json(["alice", "bob", "charlie"]);
  }),

  http.post(`${API_BASE}/api/global_chat/messages`, async ({ request }) => {
    const _data = await request.json();
    return new HttpResponse(null, { status: 200 });
  }),

  http.post(`${API_BASE}/api/direct_requests`, async ({ request }) => {
    const _data = await request.json();
    return new HttpResponse(null, { status: 200 });
  }),

  http.patch(
    `${API_BASE}/api/direct_requests/:task_id/status`,
    async ({ request }) => {
      const _data = await request.json();
      return new HttpResponse(null, { status: 200 });
    },
  ),

  http.get(`${API_BASE}/api/feeds/global_chat`, ({ request }) => {
    const url = new URL(request.url);
    const afterChatId = url.searchParams.get("after_chat_id");

    return HttpResponse.json([
      {
        sequence_name: "global_chat",
        sequence_id: (Number(afterChatId) || 0) + 1,
        event_type: "global_chat",
        payload: { id: 100, username: "bot", text: "auto-sync message" },
        created_at: new Date().toISOString(),
      },
    ]);
  }),

  http.get(`${API_BASE}/api/feeds/direct_requests`, ({ request }) => {
    const url = new URL(request.url);
    const afterRequestId = url.searchParams.get("after_request_id");

    return HttpResponse.json([
      {
        sequence_name: "direct_request",
        sequence_id: (Number(afterRequestId) || 0) + 1,
        event_type: "direct_request",
        payload: {
          id: 200,
          sender: "bot",
          recipient: "alice",
          text: "auto-sync request",
          status: "requested",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        created_at: new Date().toISOString(),
      },
    ]);
  }),
];
