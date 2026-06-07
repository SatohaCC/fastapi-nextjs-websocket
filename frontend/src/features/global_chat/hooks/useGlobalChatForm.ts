import { useRef, useState, useTransition } from "react";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import type { GlobalChatServerMessage } from "@/types/ws";

const TYPING_DEBOUNCE_MS = 500;

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
  const { send } = useWebSocketContext();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleTextChange = (value: string) => {
    setText(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (value.trim()) {
      debounceRef.current = setTimeout(() => {
        send({ type: "typing" });
      }, TYPING_DEBOUNCE_MS);
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const messageText = text.trim();
    if (!messageText) return;

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
      debounceRef.current = null;
    }

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
    setText: handleTextChange,
    handleSend,
    isSending: isPending,
  };
}
