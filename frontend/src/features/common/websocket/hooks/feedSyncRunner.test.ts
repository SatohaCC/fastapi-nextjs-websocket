import { describe, expect, it, vi } from "vitest";
import { type MutableCell, runFeedSync } from "./feedSyncRunner";

interface Feed {
  sequence_id: number;
}

/** 外部から解決できる遅延 Promise を作るヘルパー。 */
function deferred<T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
} {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((res) => {
    resolve = res;
  });
  return { promise, resolve };
}

/**
 * サーバーを模した cursor ベースのフェッチャ。
 * `seqs` のうち afterId より大きいものを seq 昇順で最大 pageSize 件返す。
 */
function makeServer(seqs: number[], pageSize = 500) {
  const calls: (number | null)[] = [];
  const fetchFeeds = (afterId: number | null): Promise<Feed[]> => {
    calls.push(afterId);
    const a = afterId ?? 0;
    const page = [...seqs]
      .filter((s) => s > a)
      .sort((x, y) => x - y)
      .slice(0, pageSize)
      .map((s) => ({ sequence_id: s }));
    return Promise.resolve(page);
  };
  return { fetchFeeds, calls };
}

function makeArgs(overrides: {
  fetchFeeds: (afterId: number | null) => Promise<Feed[]>;
  lastId?: number | null;
  isSyncing?: boolean;
  isAuthenticated?: () => boolean;
  onFeed?: (feed: Feed) => void;
  setSyncStatus?: (value: string) => void;
  maxRetries?: number;
  sleep?: (ms: number) => Promise<void>;
}) {
  const isSyncingRef: MutableCell<boolean> = {
    current: overrides.isSyncing ?? false,
  };
  const pendingSyncRef: MutableCell<boolean> = { current: false };
  const lastIdRef: MutableCell<number | null> = {
    current: overrides.lastId ?? null,
  };
  return {
    refs: { isSyncingRef, pendingSyncRef, lastIdRef },
    args: {
      isSyncingRef,
      pendingSyncRef,
      lastIdRef,
      isAuthenticated: overrides.isAuthenticated ?? (() => true),
      fetchFeeds: overrides.fetchFeeds,
      onFeed: overrides.onFeed ?? (() => {}),
      setSyncStatus: overrides.setSyncStatus ?? (() => {}),
      syncErrorMessage: "同期エラー",
      maxRetries: overrides.maxRetries,
      // テストでは待機を即時解決にしてバックオフの実時間を消す。
      sleep: overrides.sleep ?? (() => Promise.resolve()),
    },
  };
}

describe("runFeedSync", () => {
  it("未認証の場合は何もしない", async () => {
    const fetchFeeds = vi.fn(async () => [] as Feed[]);
    const { args } = makeArgs({ fetchFeeds, isAuthenticated: () => false });
    await runFeedSync(args);
    expect(fetchFeeds).not.toHaveBeenCalled();
  });

  it("取得したフィードを適用し lastId を最大値に進める", async () => {
    const applied: number[] = [];
    const { fetchFeeds, calls } = makeServer([11, 12]);
    const { refs, args } = makeArgs({
      lastId: 10,
      fetchFeeds,
      onFeed: (f) => applied.push(f.sequence_id),
    });
    await runFeedSync(args);
    expect(applied).toEqual([11, 12]);
    expect(refs.lastIdRef.current).toBe(12);
    // 11,12 を取得後、空ページ確認のため cursor=12 で1回追加取得して終了
    expect(calls).toEqual([10, 12]);
  });

  it("大きなギャップをページングで全件追従する", async () => {
    const total = 1200;
    const seqs = Array.from({ length: total }, (_, i) => i + 1); // 1..1200
    const applied: number[] = [];
    const { fetchFeeds, calls } = makeServer(seqs, 500);
    const { refs, args } = makeArgs({
      lastId: null,
      fetchFeeds,
      onFeed: (f) => applied.push(f.sequence_id),
    });
    await runFeedSync(args);
    expect(applied).toHaveLength(total);
    expect(applied[0]).toBe(1);
    expect(applied[total - 1]).toBe(total);
    expect(refs.lastIdRef.current).toBe(total);
    // 500 件ページ × 3 + 空ページ 1 = 4 回
    expect(calls).toEqual([null, 500, 1000, 1200]);
  });

  it("同期中の呼び出しは保留フラグを立てて即座に戻る", async () => {
    const fetchFeeds = vi.fn(async () => [] as Feed[]);
    const { refs, args } = makeArgs({ fetchFeeds, isSyncing: true });
    await runFeedSync(args);
    expect(fetchFeeds).not.toHaveBeenCalled();
    expect(refs.pendingSyncRef.current).toBe(true);
  });

  it("同期中に増えたフィードも取りこぼさず最終的に全件適用する", async () => {
    const first = deferred<Feed[]>();
    let firstUsed = false;
    const available = new Set<number>([11]);
    const applied: number[] = [];
    const fetchFeeds = (afterId: number | null): Promise<Feed[]> => {
      if (!firstUsed) {
        firstUsed = true;
        return first.promise; // 1回目は遅延させて「同期中」を作る
      }
      const a = afterId ?? 0;
      return Promise.resolve(
        [...available]
          .filter((s) => s > a)
          .sort((x, y) => x - y)
          .map((s) => ({ sequence_id: s })),
      );
    };

    const { refs, args } = makeArgs({
      lastId: 10,
      fetchFeeds,
      onFeed: (f) => applied.push(f.sequence_id),
    });

    const firstRun = runFeedSync(args);
    // 同期中にギャップ検知 → 2回目呼び出しは保留される。さらに新フィード 21 が出現。
    await runFeedSync(args);
    expect(refs.pendingSyncRef.current).toBe(true);
    available.add(21);

    first.resolve([{ sequence_id: 11 }]);
    await firstRun;

    expect(applied).toContain(11);
    expect(applied).toContain(21);
    expect(refs.lastIdRef.current).toBe(21);
    expect(refs.pendingSyncRef.current).toBe(false);
    expect(refs.isSyncingRef.current).toBe(false);
  });

  it("一時的な取得失敗はバックオフ再試行で回復し、データを失わない", async () => {
    const applied: number[] = [];
    const sleep = vi.fn(() => Promise.resolve());
    let failsLeft = 2; // 最初の2回は失敗、その後成功
    const server = makeServer([11, 12]);
    const fetchFeeds = (afterId: number | null): Promise<Feed[]> => {
      if (failsLeft > 0) {
        failsLeft -= 1;
        return Promise.reject(new Error("transient 503"));
      }
      return server.fetchFeeds(afterId);
    };

    const { refs, args } = makeArgs({
      lastId: 10,
      fetchFeeds,
      onFeed: (f) => applied.push(f.sequence_id),
      sleep,
    });
    await runFeedSync(args);

    expect(applied).toEqual([11, 12]); // 欠落なく全件適用
    expect(refs.lastIdRef.current).toBe(12);
    expect(sleep).toHaveBeenCalledTimes(2); // 2回の失敗ぶんだけ待機
  });

  it("リトライを使い切るとエラーメッセージを通知し、同期中フラグを解除する", async () => {
    const setSyncStatus = vi.fn();
    const fetchFeeds = vi.fn(async () => {
      throw new Error("network down");
    });
    const { refs, args } = makeArgs({
      fetchFeeds,
      setSyncStatus,
      maxRetries: 3,
    });
    await runFeedSync(args);
    // 初回 + リトライ3回 = 4 回試行してから諦める。
    expect(fetchFeeds).toHaveBeenCalledTimes(4);
    expect(setSyncStatus).toHaveBeenLastCalledWith("同期エラー");
    expect(refs.isSyncingRef.current).toBe(false);
  });

  it("リトライ中に未認証になったら即座に諦める", async () => {
    const setSyncStatus = vi.fn();
    let authed = true;
    const fetchFeeds = vi.fn(async () => {
      authed = false; // 取得失敗直後にログアウト相当
      throw new Error("network down");
    });
    const { args } = makeArgs({
      fetchFeeds,
      setSyncStatus,
      isAuthenticated: () => authed,
    });
    await runFeedSync(args);
    // 1回試行して失敗 → 未認証なのでリトライせず諦める。
    expect(fetchFeeds).toHaveBeenCalledTimes(1);
    expect(setSyncStatus).toHaveBeenLastCalledWith("同期エラー");
  });
});
