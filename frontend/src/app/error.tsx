"use client";

import { useEffect } from "react";

export default function ChatError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // biome-ignore lint/suspicious/noConsole: Error logging is necessary in the error boundary
    console.error(error);
  }, [error]);

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "24px",
        padding: "20px",
        textAlign: "center",
        background: "var(--background)",
      }}
    >
      <div
        style={{
          fontSize: "48px",
          fontWeight: "900",
          color: "var(--error)",
          letterSpacing: "-0.05em",
        }}
      >
        システムエラー
      </div>
      <p style={{ color: "var(--text-secondary)", maxWidth: "400px" }}>
        システムとの同期中に予期しないエラーが発生しました。
        サーバーとの接続が切断されています。
      </p>
      <div
        style={{
          padding: "16px",
          background: "rgba(239, 68, 68, 0.1)",
          border: "1px solid rgba(239, 68, 68, 0.2)",
          borderRadius: "12px",
          fontFamily: "monospace",
          fontSize: "12px",
          color: "var(--error)",
        }}
      >
        {error.message || "原因不明のエラーが検出されました"}
      </div>
      <button type="button" onClick={() => reset()} className="btn-primary">
        再接続を試みる
      </button>
    </div>
  );
}
