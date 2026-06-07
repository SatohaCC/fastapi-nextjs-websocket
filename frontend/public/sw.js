self.addEventListener("install", (event) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SHOW_NOTIFICATION") {
    const { title, options } = event.data;
    event.waitUntil(self.registration.showNotification(title, options));
  }
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: "window" }).then((clientList) => {
      // 優先度1: /workspace パスを含むタブを優先してフォーカス
      for (const client of clientList) {
        if (client.url.includes("/workspace") && "focus" in client) {
          return client.focus();
        }
      }
      // 優先度2: それ以外の同じオリジンのタブにフォーカス
      for (const client of clientList) {
        if ("focus" in client) {
          return client.focus();
        }
      }
      // 優先度3: タブがなければ新しく /workspace を開く
      return clients.openWindow("/workspace");
    }),
  );
});
