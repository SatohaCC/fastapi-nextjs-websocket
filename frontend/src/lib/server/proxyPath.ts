/**
 * BFF プロキシのパスセグメント検証ユーティリティ。
 *
 * catch-all ルート (`[...path]`) で受け取った各セグメントが、`/api/` 名前空間を
 * 脱出してバックエンドの他リソース（例: `/admin`）へ到達するパストラバーサルに
 * 利用されないことを保証する。
 */

/**
 * 単一のパスセグメントが安全かどうかを判定する。
 *
 * 以下のいずれかに該当する場合は不正とみなす:
 * - 空のセグメント
 * - `..`、`/`、`\` を生の状態で含む
 * - URL デコード後に `..`、`/`、`\` を含む（エンコードによる回避を防ぐ）
 * - デコードに失敗する不正なパーセントエンコーディング
 */
export function isValidPathSegment(segment: string): boolean {
  if (segment.length === 0) {
    return false;
  }

  let decoded: string;
  try {
    decoded = decodeURIComponent(segment);
  } catch {
    // 不正なパーセントエンコーディング（例: 単独の "%"）は拒否する。
    return false;
  }

  for (const value of [segment, decoded]) {
    if (value.includes("..") || value.includes("/") || value.includes("\\")) {
      return false;
    }
  }

  return true;
}

/**
 * catch-all で受け取ったパスセグメント列全体が安全かどうかを判定する。
 */
export function isValidProxyPath(path: string[]): boolean {
  return path.every(isValidPathSegment);
}
