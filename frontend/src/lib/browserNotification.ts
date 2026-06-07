export function isBrowserNotificationSupported(): boolean {
  return typeof window !== "undefined" && "Notification" in window;
}

export async function requestBrowserNotificationPermission(): Promise<boolean> {
  if (!isBrowserNotificationSupported()) return false;
  if (Notification.permission === "granted") return true;
  const result = await Notification.requestPermission();
  return result === "granted";
}

export function showBrowserNotification(title: string, body?: string): void {
  if (!isBrowserNotificationSupported()) return;
  if (Notification.permission !== "granted") return;

  // タブがアクティブでフォーカスされているときはデスクトップ通知を出さない
  if (
    typeof document !== "undefined" &&
    document.visibilityState === "visible" &&
    document.hasFocus()
  ) {
    return;
  }

  const options: NotificationOptions = {
    body,
  };

  // Service Worker コントローラーが存在する場合、postMessage で通知要求を送る。
  // これにより、非アクティブなメインスレッドからではなく、Service Worker のコンテキストから確実に通知を発生させます。
  if ("serviceWorker" in navigator && navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({
      type: "SHOW_NOTIFICATION",
      title,
      options,
    });
    return;
  }

  // フォールバック: コントローラーが存在しない場合は直接通知オブジェクトを作成
  try {
    new Notification(title, options);
  } catch (err) {
    // biome-ignore lint/suspicious/noConsole: fallback notification logging
    console.warn("Direct Notification constructor failed", err);
  }
}
