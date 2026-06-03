"use client";

import { useMemo, useOptimistic } from "react";
import { useGlobalChat } from "@/features/global_chat/hooks/useGlobalChat";
import { useGlobalChatForm } from "@/features/global_chat/hooks/useGlobalChatForm";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { useScrollToBottom } from "@/hooks/useScrollToBottom";
import type { GlobalChatServerMessage } from "@/types/ws";
import { formatDateTime } from "@/utils/date";
import { GlobalChat } from "./GlobalChat";

interface GlobalChatContainerProps {
  token: string | null;
}

export function GlobalChatContainer({ token }: GlobalChatContainerProps) {
  const { username } = useWorkspaceContext();
  const { chatMessages, sendChat } = useGlobalChat(token);

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

  const [optimisticMessages, addOptimisticMessage] = useOptimistic<
    (GlobalChatServerMessage & { isPending?: boolean })[],
    GlobalChatServerMessage & { isPending?: boolean }
  >(sortedMessages, (state, newMessage) => [...state, newMessage]);

  const { text, setText, handleSend } = useGlobalChatForm({
    onSend: sendChat,
    addOptimisticMessage,
    currentUser: username,
  });

  const bottomRef = useScrollToBottom(optimisticMessages.length);

  return (
    <GlobalChat
      messages={optimisticMessages}
      currentUser={username}
      text={text}
      onTextChange={setText}
      onSend={handleSend}
      formatTime={formatDateTime}
      bottomRef={bottomRef}
    />
  );
}
