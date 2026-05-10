import { useState } from "react";
import { formatDateTime } from "@/utils/date";

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
    return formatDateTime(dateStr);
  };

  return {
    text,
    setText,
    handleSend,
    formatTime,
  };
}
