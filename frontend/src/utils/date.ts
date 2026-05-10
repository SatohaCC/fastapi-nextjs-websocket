/**
 * 日付文字列を "MM/DD HH:mm" 形式にフォーマットします。
 * @param dateStr ISO形式などの日付文字列
 * @returns フォーマットされた文字列 (例: "05/10 18:05")
 */
export function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");

  return `${month}/${day} ${hours}:${minutes}`;
}
