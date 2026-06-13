import type {
  JoinLeaveServerMessage,
  PresenceStateServerMessage,
} from "@/types/ws";

/**
 * 在席ロスターの状態遷移（React 非依存の純粋ロジック）。
 *
 * - `presence_state`: 接続時のスナップショット。ロスター全体を置き換える。
 * - `join` / `leave`: 差分。Set への add/remove は冪等なので、
 *   多少の順序の前後やスナップショットとの重複があっても破綻しない。
 */
export type PresenceMessage =
  | PresenceStateServerMessage
  | JoinLeaveServerMessage;

/**
 * 現在の在席集合に 1 件のメッセージを適用した新しい集合を返す。
 *
 * 変化が無い場合は元の集合をそのまま返し、不要な再レンダリングを避ける。
 */
export function applyPresence(
  current: ReadonlySet<string>,
  message: PresenceMessage,
): ReadonlySet<string> {
  switch (message.type) {
    case "presence_state":
      return new Set(message.usernames);
    case "join":
      if (current.has(message.username)) return current;
      return new Set(current).add(message.username);
    case "leave": {
      if (!current.has(message.username)) return current;
      const next = new Set(current);
      next.delete(message.username);
      return next;
    }
    default:
      return current;
  }
}

/**
 * 在席集合を表示用にソートした配列へ変換する。
 */
export function toSortedUsernames(current: ReadonlySet<string>): string[] {
  return [...current].sort((a, b) => a.localeCompare(b));
}
