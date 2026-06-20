"use client";

import { useRef, useState } from "react";
import type { DirectRequestServerMessage } from "@/types/ws";

export function useDirectRequestState() {
  const [requestMessages, setRequestMessages] = useState<
    DirectRequestServerMessage[]
  >([]);
  const [isFetchingPast, setIsFetchingPast] = useState(false);
  const [hasMorePast, setHasMorePast] = useState(true);
  const lastRequestId = useRef<number | null>(null);
  return {
    requestMessages,
    setRequestMessages,
    isFetchingPast,
    setIsFetchingPast,
    hasMorePast,
    setHasMorePast,
    lastRequestId,
  };
}
