import { describe, expect, it } from "vitest";
import { getMaxId, mergeById } from "./mergeById";

describe("mergeById", () => {
  it("既存のリストに新しいアイテムをマージできる", () => {
    const prev = [
      { id: 1, text: "old 1" },
      { id: 2, text: "old 2" },
    ];
    const incoming = [{ id: 3, text: "new 3" }];
    const result = mergeById(prev, incoming);

    expect(result).toHaveLength(3);
    expect(result).toContainEqual({ id: 3, text: "new 3" });
  });

  it("ID が重複する場合、新しいアイテムで上書きされる", () => {
    const prev = [{ id: 1, text: "old 1" }];
    const incoming = [{ id: 1, text: "updated 1" }];
    const result = mergeById(prev, incoming);

    expect(result).toHaveLength(1);
    expect(result[0].text).toBe("updated 1");
  });

  it("空のリスト同士をマージしても空のリストが返る", () => {
    expect(mergeById([], [])).toEqual([]);
  });

  it("既存のリストが空の場合、新しいリストがそのまま返る", () => {
    const incoming = [{ id: 1, text: "new" }];
    expect(mergeById([], incoming)).toEqual(incoming);
  });

  it("ID が重複する場合、既存アイテムの挿入順序が保たれる", () => {
    const prev = [
      { id: 1, text: "first" },
      { id: 2, text: "second" },
    ];
    const incoming = [{ id: 1, text: "updated first" }];
    const result = mergeById(prev, incoming);

    expect(result).toHaveLength(2);
    expect(result[0]).toEqual({ id: 1, text: "updated first" });
    expect(result[1]).toEqual({ id: 2, text: "second" });
  });
});

describe("getMaxId", () => {
  it("リスト内の最大 ID を取得できる", () => {
    const items = [{ id: 10 }, { id: 5 }, { id: 20 }];
    expect(getMaxId(items)).toBe(20);
  });

  it("空リストの場合は null を返す", () => {
    expect(getMaxId([])).toBeNull();
  });
});
