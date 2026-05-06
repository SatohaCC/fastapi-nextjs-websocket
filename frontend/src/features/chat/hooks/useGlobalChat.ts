import { useState } from "react";

interface UseGlobalChatProps {
  onSend: (text: string) => void;
}

export function useGlobalChat({ onSend }: UseGlobalChatProps) {
  const [text, setText] = useState("");

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return {
    text,
    setText,
    handleSend,
    formatTime,
  };
}
