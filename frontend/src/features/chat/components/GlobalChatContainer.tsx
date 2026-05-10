"use client";

import { useGlobalChat } from "@/features/chat/hooks/useGlobalChat";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { GlobalChat } from "./GlobalChat";

export function GlobalChatContainer() {
  const { chatMessages, sendChat, username } = useWorkspaceContext();
  const { text, setText, handleSend, formatTime } = useGlobalChat({
    onSend: sendChat,
  });

  return (
    <GlobalChat
      messages={chatMessages}
      currentUser={username}
      text={text}
      onTextChange={setText}
      onSend={handleSend}
      formatTime={formatTime}
    />
  );
}
