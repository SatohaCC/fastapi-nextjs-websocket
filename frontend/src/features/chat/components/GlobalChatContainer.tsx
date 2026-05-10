"use client";

import { useGlobalChat } from "@/features/chat/hooks/useGlobalChat";
import type { ChatMessage } from "@/types/ws";
import { GlobalChat } from "./GlobalChat";

interface Props {
  messages: ChatMessage[];
  onSend: (text: string) => void;
  currentUser: string;
}

export function GlobalChatContainer({ messages, onSend, currentUser }: Props) {
  const { text, setText, handleSend, formatTime } = useGlobalChat({ onSend });

  return (
    <GlobalChat
      messages={messages}
      currentUser={currentUser}
      text={text}
      onTextChange={setText}
      onSend={handleSend}
      formatTime={formatTime}
    />
  );
}
