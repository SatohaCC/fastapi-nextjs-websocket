"use client";

import { useCallback, useMemo, useState } from "react";
import { useWsSubscribe } from "@/features/common/websocket/hooks/useWsSubscribe";
import type {
  JoinLeaveServerMessage,
  PresenceStateServerMessage,
} from "@/types/ws";
import { applyPresence, toSortedUsernames } from "../handlers/presenceReducer";

export interface UsePresenceResult {
  /** 現在オンラインのユーザー名（ソート済み）。 */
  onlineUsernames: string[];
  /** 最初の presence_state スナップショットを受信済みか。 */
  isReady: boolean;
}

/**
 * 在席ロスターを管理するフック。
 *
 * 接続時の `presence_state` スナップショットで全体を再同期し、以降は
 * `join` / `leave` 差分で更新する。
 *
 * ちらつき対策として 2 点に配慮している:
 * - スナップショット未受信（`isReady === false`）の間は「0人/誰もいない」を
 *   確定表示しない。ログイン直後の初期空状態が一瞬見えるのを防ぐ。
 * - 再接続で接続状態が一時的に切れてもロスターはクリアせず保持する（sticky）。
 *   次の `presence_state` で更新されるため、空→再表示のちらつきが起きない。
 *
 * 注: dev では React StrictMode の二重マウントにより、別ユーザーのログイン時に
 * そのクライアントが connect→disconnect→connect し、JOIN→LEAVE→JOIN が短時間に
 * 流れて一瞬ちらつくことがある。これは StrictMode 固有の挙動で、本番ビルドでは
 * 二重マウントが起きないため発生しない（新規ログインは単一 JOIN）。
 */
export function usePresence(): UsePresenceResult {
  const [online, setOnline] = useState<ReadonlySet<string>>(
    () => new Set<string>(),
  );
  const [isReady, setIsReady] = useState(false);

  const handleState = useCallback((data: PresenceStateServerMessage) => {
    setOnline((prev) => applyPresence(prev, data));
    setIsReady(true);
  }, []);
  const handleJoinLeave = useCallback((data: JoinLeaveServerMessage) => {
    setOnline((prev) => applyPresence(prev, data));
  }, []);

  useWsSubscribe<PresenceStateServerMessage>("presence_state", handleState);
  useWsSubscribe<JoinLeaveServerMessage>("join", handleJoinLeave);
  useWsSubscribe<JoinLeaveServerMessage>("leave", handleJoinLeave);

  const onlineUsernames = useMemo(() => toSortedUsernames(online), [online]);

  return { onlineUsernames, isReady };
}
