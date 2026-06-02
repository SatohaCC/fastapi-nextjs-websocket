import { useState, useTransition } from "react";
import type { GlobalChatServerMessage } from "@/types/ws";

interface UseGlobalChatFormProps {
  onSend: (text: string) => Promise<void> | void;
  addOptimisticMessage: (
    message: GlobalChatServerMessage & { isPending?: boolean },
  ) => void;
  currentUser: string;
}

export function useGlobalChatForm({
  onSend,
  addOptimisticMessage,
  currentUser,
}: UseGlobalChatFormProps) {
  const [text, setText] = useState("");
  const [isPending, startTransition] = useTransition();

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const messageText = text.trim();
    if (!messageText) return;

    // 即座に入力欄をクリア
    setText("");

    startTransition(async () => {
      // 楽観的メッセージを追加
      const tempId = -Date.now();
      addOptimisticMessage({
        type: "global_chat",
        username: currentUser,
        text: messageText,
        id: tempId,
        seq: null,
        created_at: new Date().toISOString(),
        is_history: false,
        isPending: true,
      });

      try {
        await onSend(messageText);
      } catch {
        setText(messageText);
      }
    });
  };

  return {
    text,
    setText,
    handleSend,
    isSending: isPending,
  };
}
