import { HttpResponse, http } from "msw";
import { API_BASE } from "@/lib/config";

export const handlers = [
  // ログイン API
  http.post(`${API_BASE}/api/auth/token`, () => {
    return HttpResponse.json({ access_token: "mock-token" });
  }),

  // ユーザー一覧 API
  http.get(`${API_BASE}/api/auth/users`, () => {
    return HttpResponse.json(["alice", "bob", "charlie"]);
  }),

  // メッセージ送信 API
  http.post(`${API_BASE}/api/global_chat/messages`, async ({ request }) => {
    const _data = await request.json();
    return new HttpResponse(null, { status: 200 });
  }),

  // ダイレクトリクエスト送信 API
  http.post(`${API_BASE}/api/direct_requests`, async ({ request }) => {
    const _data = await request.json();
    return new HttpResponse(null, { status: 200 });
  }),

  // ダイレクトリクエストのステータス更新 API
  http.patch(
    `${API_BASE}/api/direct_requests/:task_id/status`,
    async ({ request }) => {
      const _data = await request.json();
      return new HttpResponse(null, { status: 200 });
    },
  ),

  // フィード同期 API
  http.get(`${API_BASE}/api/feeds`, ({ request }) => {
    const url = new URL(request.url);
    const afterChatId = url.searchParams.get("after_chat_id");

    // テストケースに応じてデータを返す（今はシンプルな例）
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
];
