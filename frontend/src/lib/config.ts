export const API_BASE =
  (typeof process !== "undefined" ? process.env.NEXT_PUBLIC_API_URL : null) ||
  "http://localhost:8000";

export const WS_BASE =
  (typeof process !== "undefined" ? process.env.NEXT_PUBLIC_WS_URL : null) ||
  "ws://localhost:8000";
