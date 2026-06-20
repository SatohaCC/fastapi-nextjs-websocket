"use client";

import { useEffect, useLayoutEffect, useRef } from "react";

export interface ChatMessageLike {
  id?: number | null;
  text: string;
  isPending?: boolean;
}

/**
 * チャットおよびダイレクトリクエスト等のスクロール・アンカリング制御を行うカスタムフック。
 *
 * - 新しいメッセージ受信時（末尾追加）: 最下部へ自動スクロール
 * - 過去ログロード時（先頭追加）: scrollHeightの差分を計算してスクロール位置を維持（跳ね・ズレ防止）
 */
export function useChatScroll<T extends ChatMessageLike>(
  messages: T[],
  fetchPast: () => Promise<void>,
) {
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const contentRef = useRef<HTMLElement | null>(null);
  const scrollSnapshotRef = useRef<{
    scrollHeight: number;
    scrollTop: number;
  } | null>(null);

  const prevLastMessageRef = useRef<ChatMessageLike | null>(null);

  const handleFetchPast = async () => {
    const container = contentRef.current;
    if (container) {
      scrollSnapshotRef.current = {
        scrollHeight: container.scrollHeight,
        scrollTop: container.scrollTop,
      };
    }
    await fetchPast();
  };

  useLayoutEffect(() => {
    // Biome の useExhaustiveDependencies 警告を回避するために messages を参照します。
    const _ = messages;

    if (scrollSnapshotRef.current && contentRef.current) {
      const container = contentRef.current;
      const diff =
        container.scrollHeight - scrollSnapshotRef.current.scrollHeight;
      if (diff > 0) {
        container.scrollTop = scrollSnapshotRef.current.scrollTop + diff;
      }
      scrollSnapshotRef.current = null;
    }
  }, [messages]);

  useEffect(() => {
    if (messages.length === 0) return;
    const lastMessage = messages[messages.length - 1];

    const isDifferent =
      prevLastMessageRef.current === null ||
      prevLastMessageRef.current.id !== lastMessage.id ||
      prevLastMessageRef.current.text !== lastMessage.text ||
      prevLastMessageRef.current.isPending !== lastMessage.isPending;

    if (isDifferent) {
      bottomRef.current?.scrollIntoView({
        behavior: prevLastMessageRef.current === null ? "auto" : "smooth",
      });
    }

    prevLastMessageRef.current = {
      id: lastMessage.id,
      text: lastMessage.text,
      isPending: lastMessage.isPending,
    };
  }, [messages]);

  return {
    bottomRef,
    contentRef,
    handleFetchPast,
  };
}
