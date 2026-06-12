/**
 * フィード同期のコアロジック（React 非依存）。
 *
 * 同期実行中にギャップ復旧要求が来た場合に取りこぼさないための再同期ループを
 * 担う。React の ref は単なる `{ current }` オブジェクトなので、ここではその形の
 * 可変セルを受け取ることで、フックから独立して単体テストできるようにしている。
 */

export interface MutableCell<T> {
  current: T;
}

export interface RunFeedSyncArgs<TFeed extends { sequence_id: number }> {
  /** 同期実行中かどうかのフラグセル（呼び出し間で共有）。 */
  isSyncingRef: MutableCell<boolean>;
  /** 同期中に再同期要求が来たことを示す保留フラグセル。 */
  pendingSyncRef: MutableCell<boolean>;
  /** これまでに適用済みの最大 sequence_id。 */
  lastIdRef: MutableCell<number | null>;
  /** 認証済みかどうか。false の場合は何もしない。 */
  isAuthenticated: () => boolean;
  /** afterId 以降の欠落フィードを取得する。 */
  fetchFeeds: (afterId: number | null) => Promise<TFeed[]>;
  /** 取得した各フィードを適用する。 */
  onFeed: (feed: TFeed) => void;
  /** 同期状態メッセージを通知する。 */
  setSyncStatus: (value: string) => void;
  /** エラー時に通知するメッセージ。 */
  syncErrorMessage: string;
  /** 取得失敗時の最大リトライ回数（デフォルト 5）。 */
  maxRetries?: number;
  /** リトライの基準待機時間（ms、デフォルト 1000）。 */
  baseRetryDelayMs?: number;
  /** リトライ待機時間の上限（ms、デフォルト 30000）。 */
  maxRetryDelayMs?: number;
  /** 待機関数（テスト差し替え用）。デフォルトは setTimeout ベース。 */
  sleep?: (ms: number) => Promise<void>;
}

const DEFAULT_MAX_RETRIES = 5;
const DEFAULT_BASE_RETRY_DELAY_MS = 1000;
const DEFAULT_MAX_RETRY_DELAY_MS = 30000;

const defaultSleep = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

/**
 * 欠落フィードを取得して適用する。
 *
 * すでに同期中に呼ばれた場合は黙って捨てず `pendingSyncRef` を立てて即座に return し、
 * 進行中の同期が完了後に保留分を再同期する。これにより同期中に検知したギャップが
 * 失われない。
 */
export async function runFeedSync<TFeed extends { sequence_id: number }>(
  args: RunFeedSyncArgs<TFeed>,
): Promise<void> {
  const {
    isSyncingRef,
    pendingSyncRef,
    lastIdRef,
    isAuthenticated,
    fetchFeeds,
    onFeed,
    setSyncStatus,
    syncErrorMessage,
    maxRetries = DEFAULT_MAX_RETRIES,
    baseRetryDelayMs = DEFAULT_BASE_RETRY_DELAY_MS,
    maxRetryDelayMs = DEFAULT_MAX_RETRY_DELAY_MS,
    sleep = defaultSleep,
  } = args;

  if (!isAuthenticated()) return;
  // 同期中に呼ばれた場合は保留して、完了後に再実行させる。
  if (isSyncingRef.current) {
    pendingSyncRef.current = true;
    return;
  }

  // 1 ページの取得を、失敗時に指数バックオフでリトライする。これにより一時的な
  // ネットワーク断や 5xx で復旧が中断したまま穴が残るのを防ぐ。リトライを使い切るか、
  // 途中で未認証（ログアウト等）になった場合は例外を送出して呼び出し側の catch に委ねる。
  const fetchPageWithRetry = async (
    afterId: number | null,
  ): Promise<TFeed[]> => {
    let attempt = 0;
    while (true) {
      try {
        return await fetchFeeds(afterId);
      } catch (error) {
        attempt += 1;
        if (!isAuthenticated() || attempt > maxRetries) throw error;
        setSyncStatus(
          `同期に失敗しました。再試行中... (${attempt}/${maxRetries})`,
        );
        const delay = Math.min(
          baseRetryDelayMs * 2 ** (attempt - 1),
          maxRetryDelayMs,
        );
        await sleep(delay);
      }
    }
  };

  isSyncingRef.current = true;
  try {
    // 同期中に新たなギャップを取りこぼしていた場合は、最新の lastIdRef を起点に
    // 再同期する。保留がなくなるまで繰り返す。
    do {
      pendingSyncRef.current = false;
      // ページング: サーバーは 1 回の取得を一定件数で打ち切るため、cursor を進めて
      // 空ページになるまで取得し続ける。これにより巨大なギャップでも全件追従しつつ、
      // 単一レスポンスのサイズは境界化される。
      while (true) {
        const before = lastIdRef.current;
        const feeds = await fetchPageWithRetry(before);
        if (feeds.length === 0) break;
        for (const feed of feeds) {
          onFeed(feed);
          if (feed.sequence_id > (lastIdRef.current ?? -1)) {
            lastIdRef.current = feed.sequence_id;
          }
        }
        // cursor が進まない（想定外）の場合は無限ループ防止で打ち切る。
        if (lastIdRef.current === before) break;
      }
      setSyncStatus(`最終同期: ${new Date().toLocaleTimeString()}`);
    } while (pendingSyncRef.current);
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[useFeedSync] Sync error:", error);
    setSyncStatus(syncErrorMessage);
  } finally {
    isSyncingRef.current = false;
  }
}
