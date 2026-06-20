import { describe, expect, it } from "vitest";
import { isValidPathSegment, isValidProxyPath } from "./proxyPath";

describe("isValidPathSegment", () => {
  it("accepts normal segments", () => {
    expect(isValidPathSegment("rooms")).toBe(true);
    expect(isValidPathSegment("123")).toBe(true);
    expect(isValidPathSegment("user-profile")).toBe(true);
    // パーセントエンコードされた通常文字（スペース等）は許可する。
    expect(isValidPathSegment("hello%20world")).toBe(true);
  });

  it("rejects empty segments", () => {
    expect(isValidPathSegment("")).toBe(false);
  });

  it("rejects raw traversal sequences", () => {
    expect(isValidPathSegment("..")).toBe(false);
    expect(isValidPathSegment("../admin")).toBe(false);
    expect(isValidPathSegment("foo/bar")).toBe(false);
    expect(isValidPathSegment("foo\\bar")).toBe(false);
  });

  it("rejects percent-encoded traversal sequences", () => {
    // ".." -> %2e%2e
    expect(isValidPathSegment("%2e%2e")).toBe(false);
    expect(isValidPathSegment("%2E%2E")).toBe(false);
    // "/" -> %2f, "\" -> %5c
    expect(isValidPathSegment("%2f")).toBe(false);
    expect(isValidPathSegment("%2F")).toBe(false);
    expect(isValidPathSegment("%5c")).toBe(false);
    // "../" -> %2e%2e%2f
    expect(isValidPathSegment("%2e%2e%2f")).toBe(false);
  });

  it("rejects malformed percent-encoding", () => {
    expect(isValidPathSegment("%")).toBe(false);
    expect(isValidPathSegment("%zz")).toBe(false);
    expect(isValidPathSegment("foo%")).toBe(false);
  });
});

describe("isValidProxyPath", () => {
  it("accepts a path of valid segments", () => {
    expect(isValidProxyPath(["rooms", "42", "messages"])).toBe(true);
  });

  it("accepts an empty path array", () => {
    expect(isValidProxyPath([])).toBe(true);
  });

  it("rejects when any segment is invalid", () => {
    expect(isValidProxyPath(["rooms", "..", "admin"])).toBe(false);
    expect(isValidProxyPath(["rooms", "%2e%2e", "admin"])).toBe(false);
    expect(isValidProxyPath(["rooms", ""])).toBe(false);
  });

  it("blocks the reported escape to the /admin namespace", () => {
    // エンコードした ".." で /api/ を脱出して /admin へ到達する攻撃を遮断する。
    expect(isValidProxyPath(["%2e%2e", "admin"])).toBe(false);
  });
});
