/**
 * 既存のリストに新しいアイテムをマージし、ID で重複排除＋ソートする。
 * WebSocket のリアルタイムメッセージと REST の同期データの統合に使用。
 */
export function mergeById<T extends { id: number }>(
  prev: T[],
  incoming: T[],
): T[] {
  const map = new Map(prev.map((item) => [item.id, item]));
  for (const item of incoming) {
    map.set(item.id, item);
  }
  return Array.from(map.values()).sort((a, b) => a.id - b.id);
}

/**
 * リスト内の最大 ID を返す。空の場合は null。
 */
export function getMaxId<T extends { id: number }>(items: T[]): number | null {
  if (items.length === 0) return null;
  return Math.max(...items.map((item) => item.id));
}
