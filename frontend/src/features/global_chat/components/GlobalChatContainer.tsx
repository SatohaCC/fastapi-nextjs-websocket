"use client";

import { useMemo, useOptimistic } from "react";
import { useGlobalChat } from "@/features/global_chat/hooks/useGlobalChat";
import { useGlobalChatForm } from "@/features/global_chat/hooks/useGlobalChatForm";
import { useMentionDropdown } from "@/features/global_chat/hooks/useMentionDropdown";
import { useTypingIndicator } from "@/features/global_chat/hooks/useTypingIndicator";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { useScrollToBottom } from "@/hooks/useScrollToBottom";
import type { GlobalChatServerMessage } from "@/types/ws";
import { formatDateTime } from "@/utils/date";
import { GlobalChat } from "./GlobalChat";

export function GlobalChatContainer() {
  const { username, users } = useWorkspaceContext();
  // ワークスペース内は常に認証済みであるため true を渡します
  const { chatMessages, sendChat } = useGlobalChat(true);

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

  const { typingUsers } = useTypingIndicator(username);

  const {
    isOpen: mentionIsOpen,
    suggestions: mentionSuggestions,
    focusedIndex: mentionFocusedIndex,
    handleMentionSelect,
    handleInputKeyDown,
    handleInputChange,
  } = useMentionDropdown({
    text,
    users,
    currentUser: username,
    onTextChange: setText,
  });

  const bottomRef = useScrollToBottom(optimisticMessages.length);

  return (
    <GlobalChat
      messages={optimisticMessages}
      currentUser={username}
      text={text}
      onTextChange={handleInputChange}
      onSend={handleSend}
      onInputKeyDown={handleInputKeyDown}
      formatTime={formatDateTime}
      bottomRef={bottomRef}
      typingUsers={typingUsers}
      mentionIsOpen={mentionIsOpen}
      mentionSuggestions={mentionSuggestions}
      mentionFocusedIndex={mentionFocusedIndex}
      onMentionSelect={handleMentionSelect}
    />
  );
}
