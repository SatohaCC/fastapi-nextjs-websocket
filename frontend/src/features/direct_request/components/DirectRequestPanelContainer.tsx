"use client";

import { useMemo, useOptimistic } from "react";
import { useDirectRequest } from "@/features/direct_request/hooks/useDirectRequest";
import { useDirectRequestForm } from "@/features/direct_request/hooks/useDirectRequestForm";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { useScrollToBottom } from "@/hooks/useScrollToBottom";
import type { DirectRequestServerMessage } from "@/types/ws";
import { formatDateTime } from "@/utils/date";
import { DirectRequestPanel } from "./DirectRequestPanel";

export function DirectRequestPanelContainer() {
  const { users, username } = useWorkspaceContext();
  // ワークスペース内は常に認証済みであるため true を渡します
  const { requestMessages, sendRequest, updateStatus } = useDirectRequest(true);

  const otherUsers = useMemo(
    () => users.filter((u) => u !== username),
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
    });

  const bottomRef = useScrollToBottom(optimisticRequests.length);

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
      isSending={isSending}
    />
  );
}
