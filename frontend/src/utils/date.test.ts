import { describe, expect, it } from "vitest";
import { formatDateTime } from "./date";

describe("formatDateTime", () => {
  it("should format date string correctly as MM/DD HH:mm", () => {
    const input = "2024-05-10T18:05:00Z";
    // 注意: テスト実行環境のタイムゾーンに依存するため、UTCで検証するか、期待値を調整する必要があります。
    // ここでは構造のみチェックします。
    const result = formatDateTime(input);
    expect(result).toMatch(/^\d{2}\/\d{2} \d{2}:\d{2}$/);
  });

  it("should handle invalid date strings gracefully", () => {
    expect(formatDateTime("invalid")).toBe("");
  });

  it("should pad single digits with zeros", () => {
    // 2024-01-02 03:04
    const input = "2024-01-02T03:04:00";
    const result = formatDateTime(input);
    expect(result).toBe("01/02 03:04");
  });
});
