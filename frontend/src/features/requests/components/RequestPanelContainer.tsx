"use client";

import { useMemo } from "react";
import { useRequestPanel } from "@/features/requests/hooks/useRequestPanel";
import type { RequestMessage, RequestStatus } from "@/types/ws";
import { RequestPanel } from "./RequestPanel";

interface Props {
  users: string[];
  messages: RequestMessage[];
  onSend: (to: string, text: string) => void;
  onUpdateStatus: (id: number, status: RequestStatus) => void;
  currentUser: string;
}

export function RequestPanelContainer({
  users,
  messages,
  onSend,
  onUpdateStatus,
  currentUser,
}: Props) {
  const { targetUser, setTargetUser, text, setText, handleSend, formatDate } =
    useRequestPanel({ onSend });

  const otherUsers = users.filter((u) => u !== currentUser);

  // データ加工ロジック（反転）を Container 側で担当
  const reversedMessages = useMemo(() => {
    return [...messages].reverse();
  }, [messages]);

  return (
    <RequestPanel
      otherUsers={otherUsers}
      messages={reversedMessages}
      currentUser={currentUser}
      targetUser={targetUser}
      text={text}
      onTargetUserChange={setTargetUser}
      onTextChange={setText}
      onSend={handleSend}
      onUpdateStatus={onUpdateStatus}
      formatDate={formatDate}
    />
  );
}
