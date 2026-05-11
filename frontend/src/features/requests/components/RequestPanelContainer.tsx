"use client";

import { useMemo } from "react";
import { useRequestPanel } from "@/features/requests/hooks/useRequestPanel";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { RequestPanel } from "./RequestPanel";

export function RequestPanelContainer() {
  const { users, requestMessages, sendRequest, updateStatus, username } =
    useWorkspaceContext();

  const { targetUser, setTargetUser, text, setText, handleSend, formatDate } =
    useRequestPanel({ onSend: sendRequest });

  const otherUsers = users.filter((u) => u !== username);

  // データ加工ロジック（反転）を Container 側で担当
  const reversedMessages = useMemo(() => {
    return [...requestMessages].reverse();
  }, [requestMessages]);

  return (
    <RequestPanel
      otherUsers={otherUsers}
      messages={reversedMessages}
      currentUser={username}
      targetUser={targetUser}
      text={text}
      onTargetUserChange={setTargetUser}
      onTextChange={setText}
      onSend={handleSend}
      onUpdateStatus={updateStatus}
      formatDate={formatDate}
    />
  );
}
