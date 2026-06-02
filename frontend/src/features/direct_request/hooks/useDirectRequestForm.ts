import { useState, useTransition } from "react";
import type { DirectRequestServerMessage } from "@/types/ws";

interface UseDirectRequestFormProps {
  onSend: (to: string, text: string) => Promise<void> | void;
  addOptimisticRequest: (
    request: DirectRequestServerMessage & { isPending?: boolean },
  ) => void;
  currentUser: string;
}

export function useDirectRequestForm({
  onSend,
  addOptimisticRequest,
  currentUser,
}: UseDirectRequestFormProps) {
  const [targetUser, setTargetUser] = useState("");
  const [text, setText] = useState("");
  const [isPending, startTransition] = useTransition();

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const requestText = text.trim();
    if (!targetUser || !requestText) return;

    // 即座に入力欄をクリア
    setText("");

    startTransition(async () => {
      // 楽観的リクエストを追加
      const tempId = -Date.now();
      addOptimisticRequest({
        type: "direct_request",
        id: tempId,
        seq: null,
        sender: currentUser,
        recipient: targetUser,
        text: requestText,
        status: "requested",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_history: false,
        isPending: true,
      });

      try {
        await onSend(targetUser, requestText);
      } catch {
        setText(requestText);
      }
    });
  };

  return {
    targetUser,
    setTargetUser,
    text,
    setText,
    handleSend,
    isSending: isPending,
  };
}
