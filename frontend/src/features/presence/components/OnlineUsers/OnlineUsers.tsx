import {
  barStyles,
  chipStyles,
  countDotStyles,
  emptyStyles,
  labelStyles,
  listStyles,
} from "./OnlineUsers.styles";

interface OnlineUsersProps {
  usernames: string[];
  currentUsername?: string;
  /** 在席スナップショットを受信済みか。false の間はローディング表示にする。 */
  isReady?: boolean;
}

/**
 * 現在オンラインのユーザーをチップで一覧表示する Presentational コンポーネント。
 * ロジックは持たず、受け取った配列を表示するだけ。
 *
 * `isReady` が false（スナップショット未受信）の間は「0人/誰もいない」を出さず、
 * ローディング表示にしてログイン直後のちらつきを防ぐ。
 */
export function OnlineUsers({
  usernames,
  currentUsername,
  isReady = true,
}: OnlineUsersProps) {
  if (!isReady) {
    return (
      <section className={barStyles} aria-busy="true" aria-live="polite">
        <span className={labelStyles}>
          <span className={countDotStyles} aria-hidden="true" />
          オンライン状況を取得中…
        </span>
      </section>
    );
  }

  return (
    <section
      className={barStyles}
      aria-label={`オンラインのユーザー: ${usernames.length}人`}
    >
      <span className={labelStyles}>
        <span className={countDotStyles} aria-hidden="true" />
        オンライン ({usernames.length})
      </span>
      {usernames.length === 0 ? (
        <span className={emptyStyles}>誰もオンラインではありません</span>
      ) : (
        <ul className={listStyles}>
          {usernames.map((name) => {
            const isSelf = name === currentUsername;
            return (
              <li
                key={name}
                className={chipStyles({ self: isSelf })}
                aria-label={isSelf ? `${name}（あなた）` : name}
              >
                {name}
                {isSelf && "（あなた）"}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
