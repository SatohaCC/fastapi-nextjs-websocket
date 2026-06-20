"use client";

import { useRef, useState } from "react";
import type { GlobalChatServerMessage } from "@/types/ws";

export function useGlobalChatState() {
  const [chatMessages, setChatMessages] = useState<GlobalChatServerMessage[]>(
    [],
  );
  const [isFetchingPast, setIsFetchingPast] = useState(false);
  const [hasMorePast, setHasMorePast] = useState(true);
  const lastChatId = useRef<number | null>(null);
  return {
    chatMessages,
    setChatMessages,
    isFetchingPast,
    setIsFetchingPast,
    hasMorePast,
    setHasMorePast,
    lastChatId,
  };
}
