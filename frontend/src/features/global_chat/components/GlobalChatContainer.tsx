"use client";

import { useMemo } from "react";
import { useGlobalChatForm } from "@/features/global_chat/hooks/useGlobalChatForm";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { formatDateTime } from "@/utils/date";
import { GlobalChat } from "./GlobalChat";

export function GlobalChatContainer() {
  const { chatMessages, sendChat, username } = useWorkspaceContext();
  const { text, setText, handleSend } = useGlobalChatForm({
    onSend: sendChat,
  });

  // seq が無い（履歴）場合は id でソートし、seq がある場合は seq でソートする
  const sortedMessages = useMemo(
    () =>
      [...chatMessages].sort((a, b) => {
        const aSeq = a.seq ?? 0;
        const bSeq = b.seq ?? 0;
        if (aSeq !== bSeq) return aSeq - bSeq;
        return (a.id ?? 0) - (b.id ?? 0);
      }),
    [chatMessages],
  );

  return (
    <GlobalChat
      messages={sortedMessages}
      currentUser={username}
      text={text}
      onTextChange={setText}
      onSend={handleSend}
      formatTime={formatDateTime}
    />
  );
}
