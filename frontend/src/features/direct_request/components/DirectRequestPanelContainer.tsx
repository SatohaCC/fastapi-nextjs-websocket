"use client";

import { useMemo } from "react";
import { useDirectRequest } from "@/features/direct_request/hooks/useDirectRequest";
import { useDirectRequestForm } from "@/features/direct_request/hooks/useDirectRequestForm";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { useScrollToBottom } from "@/hooks/useScrollToBottom";
import { formatDateTime } from "@/utils/date";
import { DirectRequestPanel } from "./DirectRequestPanel";

interface DirectRequestPanelContainerProps {
  token: string | null;
}

export function DirectRequestPanelContainer({
  token,
}: DirectRequestPanelContainerProps) {
  const { users, username } = useWorkspaceContext();
  const { requestMessages, sendRequest, updateStatus } =
    useDirectRequest(token);

  const { targetUser, setTargetUser, text, setText, handleSend, isSending } =
    useDirectRequestForm({ onSend: sendRequest });

  const otherUsers = users.filter((u) => u !== username);

  const displayRequests = useMemo(
    () => [...requestMessages].sort((a, b) => (a.id ?? 0) - (b.id ?? 0)),
    [requestMessages],
  );

  const bottomRef = useScrollToBottom(displayRequests.length);

  return (
    <DirectRequestPanel
      otherUsers={otherUsers}
      requests={displayRequests}
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
