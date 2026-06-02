import { useState } from "react";

interface UseDirectRequestFormProps {
  onSend: (to: string, text: string) => Promise<void> | void;
}

export function useDirectRequestForm({ onSend }: UseDirectRequestFormProps) {
  const [targetUser, setTargetUser] = useState("");
  const [text, setText] = useState("");
  const [isSending, setIsSending] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUser || !text.trim() || isSending) return;
    setIsSending(true);
    try {
      await onSend(targetUser, text);
      setText("");
    } catch {
      // エラー時は入力を維持するため、setText("") を実行しない
    } finally {
      setIsSending(false);
    }
  };

  return {
    targetUser,
    setTargetUser,
    text,
    setText,
    handleSend,
    isSending,
  };
}
