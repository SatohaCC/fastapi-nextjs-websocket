import { useState } from "react";
import { formatDateTime } from "@/utils/date";

interface UseDirectRequestPanelProps {
  onSend: (to: string, text: string) => void;
}

export function useDirectRequestPanel({ onSend }: UseDirectRequestPanelProps) {
  const [targetUser, setTargetUser] = useState("");
  const [text, setText] = useState("");

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUser || !text.trim()) return;
    onSend(targetUser, text);
    setText("");
  };

  const formatDate = (dateStr: string) => {
    return formatDateTime(dateStr);
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
