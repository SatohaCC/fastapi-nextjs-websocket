"use client";

import { useCallback, useState } from "react";
import {
  sendRequest as apiSendRequest,
  updateRequestStatus,
} from "@/features/websocket/api";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import type { RequestStatus } from "@/types/ws";
import { formatDateTime } from "@/utils/date";

/**
 * リクエスト機能のUI状態とアクションを統合したフック
 */
export function useRequests() {
  const { authToken } = useWorkspaceContext();
  const [targetUser, setTargetUser] = useState("");
  const [text, setText] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!targetUser || !text.trim() || !authToken) return;

      setIsProcessing(true);
      setError(null);
      try {
        await apiSendRequest(authToken, { to: targetUser, text });
        setText("");
      } catch (err) {
        setError("リクエストの送信に失敗しました");
      } finally {
        setIsProcessing(false);
      }
    },
    [targetUser, text, authToken],
  );

  const updateStatus = useCallback(
    async (requestId: number, status: RequestStatus) => {
      if (!authToken) return;

      setIsProcessing(true);
      setError(null);
      try {
        await updateRequestStatus(authToken, requestId, status);
      } catch (err) {
        setError("ステータスの更新に失敗しました");
      } finally {
        setIsProcessing(false);
      }
    },
    [authToken],
  );

  const formatDate = (dateStr: string) => {
    return formatDateTime(dateStr);
  };

  return {
    targetUser,
    setTargetUser,
    text,
    setText,
    handleSend,
    updateStatus,
    isProcessing,
    error,
    formatDate,
  };
}
