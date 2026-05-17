"use client";

import { useMemo } from "react";
import { useDirectRequest } from "@/features/direct_request/hooks/useDirectRequest";
import { useDirectRequestForm } from "@/features/direct_request/hooks/useDirectRequestForm";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
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

  const { targetUser, setTargetUser, text, setText, handleSend } =
    useDirectRequestForm({ onSend: sendRequest });

  const otherUsers = users.filter((u) => u !== username);

  const displayRequests = useMemo(
    () =>
      [...requestMessages]
        .sort((a, b) => {
          const aSeq = a.seq ?? 0;
          const bSeq = b.seq ?? 0;
          if (aSeq !== bSeq) return aSeq - bSeq;
          return (a.id ?? 0) - (b.id ?? 0);
        })
        .reverse(),
    [requestMessages],
  );

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
    />
  );
}
