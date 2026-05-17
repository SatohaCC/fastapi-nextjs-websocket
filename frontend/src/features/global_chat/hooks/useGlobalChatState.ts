"use client";

import { useRef, useState } from "react";
import type { GlobalChatServerMessage } from "@/types/ws";

export function useGlobalChatState() {
  const [chatMessages, setChatMessages] = useState<GlobalChatServerMessage[]>(
    [],
  );
  const lastChatId = useRef<number | null>(null);
  return { chatMessages, setChatMessages, lastChatId };
}
