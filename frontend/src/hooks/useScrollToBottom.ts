"use client";

import { useEffect, useRef } from "react";

export function useScrollToBottom(length: number) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const prevLengthRef = useRef(length);

  useEffect(() => {
    if (length > prevLengthRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
    prevLengthRef.current = length;
  }, [length]);

  return bottomRef;
}
