import { HttpResponse, http } from "msw";

export const handlers = [
  http.post("/api/auth/login", () => {
    return HttpResponse.json({
      id: "019ee302-bef2-76c5-9b43-ffe42e94fa95",
      userid: "testuser",
      username: "testuser",
    });
  }),

  http.post("/api/auth/refresh", () => {
    return HttpResponse.json({
      access_token: "mock-new-access-token",
      refresh_token: "mock-new-refresh-token",
      token_type: "bearer",
    });
  }),

  http.post("/api/auth/logout", () => {
    return HttpResponse.json({ success: true });
  }),

  http.get("/api/auth/me", () => {
    const id = "019ee302-bef2-76c5-9b43-ffe42e94fa95";
    const userid =
      (typeof sessionStorage !== "undefined" &&
        sessionStorage.getItem("userid")) ||
      "alice";
    const username =
      (typeof sessionStorage !== "undefined" &&
        sessionStorage.getItem("username")) ||
      "alice";
    return HttpResponse.json({ id, userid, username });
  }),

  http.get("/api/auth/ws-ticket", () => {
    return HttpResponse.json({ ticket: "mock-ticket-1234" });
  }),

  http.get("/api/proxy/auth/users", () => {
    return HttpResponse.json([
      { id: "019ee302-bef2-76c5-9b43-ffe42e94fa95", username: "alice" },
      { id: "019ee302-bef2-76c5-9b43-ffe42e94fa96", username: "bob" },
      { id: "019ee302-bef2-76c5-9b43-ffe42e94fa97", username: "charlie" },
    ]);
  }),

  http.get("/api/proxy/user_settings", () => {
    return HttpResponse.json({
      global_chat: true,
      direct_request: true,
      direct_request_updated: true,
    });
  }),

  http.put("/api/proxy/user_settings", async () => {
    return new HttpResponse(null, { status: 200 });
  }),

  http.post("/api/proxy/global_chat/messages", async () => {
    return new HttpResponse(null, { status: 200 });
  }),

  http.post("/api/proxy/direct_requests", async () => {
    return new HttpResponse(null, { status: 200 });
  }),

  http.patch("/api/proxy/direct_requests/:task_id/status", async () => {
    return new HttpResponse(null, { status: 200 });
  }),

  http.get("/api/proxy/feeds/global_chat", ({ request }) => {
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

  http.get("/api/proxy/feeds/direct_requests", ({ request }) => {
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
