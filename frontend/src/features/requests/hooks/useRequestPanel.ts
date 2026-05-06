import { useState } from "react";

interface UseRequestPanelProps {
  onSend: (to: string, text: string) => void;
}

export function useRequestPanel({ onSend }: UseRequestPanelProps) {
  const [targetUser, setTargetUser] = useState("");
  const [text, setText] = useState("");

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUser || !text.trim()) return;
    onSend(targetUser, text);
    setText("");
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return {
    targetUser,
    setTargetUser,
    text,
    setText,
    handleSend,
    formatDate,
  };
}
