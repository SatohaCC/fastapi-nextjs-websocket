"use client";

import { useCallback, useState } from "react";
import { sendMessage } from "@/features/websocket/api";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { formatDateTime } from "@/utils/date";

/**
 * チャット機能のUI状態とアクションを統合したフック
 */
export function useChat() {
  const { authToken } = useWorkspaceContext();
  const [text, setText] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!text.trim() || !authToken) return;

      setIsSending(true);
      setError(null);
      try {
        await sendMessage(authToken, text);
        setText("");
      } catch (err) {
        setError("メッセージの送信に失敗しました");
      } finally {
        setIsSending(false);
      }
    },
    [text, authToken],
  );

  const formatTime = (dateStr: string) => {
    return formatDateTime(dateStr);
  };

  return {
    text,
    setText,
    handleSend,
    isSending,
    error,
    formatTime,
  };
}
