import { useState } from "react";

interface UseDirectRequestFormProps {
  onSend: (to: string, text: string) => void;
}

export function useDirectRequestForm({ onSend }: UseDirectRequestFormProps) {
  const [targetUser, setTargetUser] = useState("");
  const [text, setText] = useState("");

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUser || !text.trim()) return;
    onSend(targetUser, text);
    setText("");
  };

  return {
    targetUser,
    setTargetUser,
    text,
    setText,
    handleSend,
  };
}
