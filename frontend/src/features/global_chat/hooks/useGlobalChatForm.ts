import { useState } from "react";

interface UseGlobalChatFormProps {
  onSend: (text: string) => void;
}

export function useGlobalChatForm({ onSend }: UseGlobalChatFormProps) {
  const [text, setText] = useState("");

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return {
    text,
    setText,
    handleSend,
  };
}
