export const API_BASE =
  (typeof process !== "undefined" ? process.env.NEXT_PUBLIC_API_URL : null) ||
  "http://127.0.0.1:8000";

export const WS_BASE =
  (typeof process !== "undefined" ? process.env.NEXT_PUBLIC_WS_URL : null) ||
  "ws://127.0.0.1:8000";

export const SYNC_INTERVAL_MS = 30_000;
