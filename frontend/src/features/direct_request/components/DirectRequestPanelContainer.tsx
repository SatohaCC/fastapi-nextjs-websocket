"use client";

import { useMemo } from "react";
import { useDirectRequestPanel } from "@/features/direct_request/hooks/useDirectRequestPanel";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { DirectRequestPanel } from "./DirectRequestPanel";

export function DirectRequestPanelContainer() {
  const { users, requestMessages, sendRequest, updateStatus, username } =
    useWorkspaceContext();

  const { targetUser, setTargetUser, text, setText, handleSend, formatDate } =
    useDirectRequestPanel({ onSend: sendRequest });

  const otherUsers = users.filter((u) => u !== username);

  // seq が無い（履歴）場合は id でソートし、seq がある場合は seq でソートする。
  // 表示は新しい順なので最後に reverse する
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
      formatDate={formatDate}
    />
  );
}
