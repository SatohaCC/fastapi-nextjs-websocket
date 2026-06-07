"use client";

import { useCallback, useState } from "react";
import { useWsSubscribe } from "@/features/common/websocket/hooks/useWsSubscribe";
import type { StopTypingServerMessage, TypingServerMessage } from "@/types/ws";

/**
 * グローバルチャットの入力中ユーザー一覧を管理するフック。
 * サーバーが typing / stop_typing を自動ブロードキャストするため、フロントにタイマー不要。
 */
export function useTypingIndicator(currentUsername: string) {
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set());

  const handleTyping = useCallback(
    (data: TypingServerMessage) => {
      if (data.username === currentUsername) return;
      setTypingUsers((prev) => new Set([...prev, data.username]));
    },
    [currentUsername],
  );

  const handleStopTyping = useCallback((data: StopTypingServerMessage) => {
    setTypingUsers((prev) => {
      const next = new Set(prev);
      next.delete(data.username);
      return next;
    });
  }, []);

  useWsSubscribe<TypingServerMessage>("typing", handleTyping);
  useWsSubscribe<StopTypingServerMessage>("stop_typing", handleStopTyping);

  return { typingUsers };
}
