"use client";

import { useMemo, useOptimistic } from "react";
import { useDirectRequestContext } from "@/features/direct_request/context/DirectRequestContext";
import { useDirectRequestForm } from "@/features/direct_request/hooks/useDirectRequestForm";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { useChatScroll } from "@/hooks/useChatScroll";
import type { DirectRequestServerMessage } from "@/types/ws";
import { formatDateTime } from "@/utils/date";
import { DirectRequestPanel } from "./DirectRequestPanel";

export function DirectRequestPanelContainer() {
  const { users, username } = useWorkspaceContext();
  const {
    requestMessages,
    sendRequest,
    updateStatus,
    fetchPastRequests,
    isFetchingPast,
    hasMorePast,
  } = useDirectRequestContext();

  const otherUsers = useMemo(
    () => users.filter((u) => u.username !== username),
    [users, username],
  );

  const displayRequests = useMemo(
    () => [...requestMessages].sort((a, b) => (a.id ?? 0) - (b.id ?? 0)),
    [requestMessages],
  );

  const [optimisticRequests, addOptimisticRequest] = useOptimistic<
    (DirectRequestServerMessage & { isPending?: boolean })[],
    DirectRequestServerMessage & { isPending?: boolean }
  >(displayRequests, (state, newRequest) => [...state, newRequest]);

  const { targetUser, setTargetUser, text, setText, handleSend, isSending } =
    useDirectRequestForm({
      onSend: sendRequest,
      addOptimisticRequest,
      currentUser: username,
      users,
    });

  const { bottomRef, contentRef, handleFetchPast } = useChatScroll(
    optimisticRequests,
    fetchPastRequests,
  );

  return (
    <DirectRequestPanel
      otherUsers={otherUsers}
      requests={optimisticRequests}
      currentUser={username}
      targetUser={targetUser}
      text={text}
      onTargetUserChange={setTargetUser}
      onTextChange={setText}
      onSend={handleSend}
      onUpdateStatus={updateStatus}
      formatDate={formatDateTime}
      bottomRef={bottomRef}
      contentRef={contentRef}
      onFetchPast={handleFetchPast}
      isFetchingPast={isFetchingPast}
      hasMorePast={hasMorePast}
      isSending={isSending}
    />
  );
}
