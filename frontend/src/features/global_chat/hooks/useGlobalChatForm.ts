import { useState } from "react";

interface UseGlobalChatFormProps {
  onSend: (text: string) => Promise<void> | void;
}

export function useGlobalChatForm({ onSend }: UseGlobalChatFormProps) {
  const [text, setText] = useState("");
  const [isSending, setIsSending] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || isSending) return;
    setIsSending(true);
    try {
      await onSend(text);
      setText("");
    } catch {
      // エラー時は入力を維持するため、setText("") を実行しない
    } finally {
      setIsSending(false);
    }
  };

  return {
    text,
    setText,
    handleSend,
    isSending,
  };
}
