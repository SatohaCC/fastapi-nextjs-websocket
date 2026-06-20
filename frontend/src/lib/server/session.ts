import "server-only";
import crypto from "node:crypto";
import { headers } from "next/headers";
import { API_BASE } from "@/lib/config";

const ALGORITHM = "aes-256-gcm";
const IV_LENGTH = 12;

const resolveSecretKey = (): string => {
  const secret = process.env.BFF_SECRET;
  if (secret) {
    return secret;
  }
  if (process.env.NODE_ENV === "production") {
    throw new Error(
      "BFF_SECRET must be set in production (see frontend/.env.example)",
    );
  }
  return "dev-secret-key-32-bytes-long-1234567";
};

const SECRET_KEY = resolveSecretKey();

export const SESSION_COOKIE = "bff_session";
export const REFRESH_COOKIE = "bff_refresh";

export const SESSION_COOKIE_OPTIONS = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
  maxAge: 60 * 14, // JWT有効期限(15分)より1分短く設定
};

export const REFRESH_COOKIE_OPTIONS = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
  maxAge: 60 * 60 * 24 * 7,
};

const getSecretKey = (): Buffer => {
  return crypto.createHash("sha256").update(SECRET_KEY).digest();
};

/**
 * トークンを暗号化してセッション用文字列を生成します。
 *
 * @param token 生のアクセストークン
 * @returns 暗号化されたセッション文字列
 */
export async function encryptSession(token: string): Promise<string> {
  const iv = crypto.randomBytes(IV_LENGTH);
  const key = getSecretKey();
  const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

  let encrypted = cipher.update(token, "utf8", "hex");
  encrypted += cipher.final("hex");

  const authTag = cipher.getAuthTag();

  return `${iv.toString("hex")}:${encrypted}:${authTag.toString("hex")}`;
}

/**
 * セッション文字列を復号して生のトークンを取り出します。
 *
 * @param sessionVal 暗号化されたセッション文字列
 * @returns 復号された生のトークン、または失敗時は null
 */
export async function decryptSession(
  sessionVal: string,
): Promise<string | null> {
  try {
    const parts = sessionVal.split(":");
    if (parts.length !== 3) return null;

    const [ivHex, encryptedHex, authTagHex] = parts;
    const iv = Buffer.from(ivHex, "hex");
    const authTag = Buffer.from(authTagHex, "hex");

    const key = getSecretKey();
    const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encryptedHex, "hex", "utf8");
    decrypted += decipher.final("utf8");

    return decrypted;
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[decryptSession] Decryption failed:", error);
    return null;
  }
}

export interface RefreshedTokens {
  encryptedAccess: string;
  encryptedRefresh: string;
}

export interface RefreshResult {
  accessToken: string;
  encryptedAccess: string;
  encryptedRefresh: string;
}

/**
 * セッション関連の Cookie をすべて削除します。
 *
 * ログアウト時のほか、トークンが無効と確定した（再ログインが必要な）場合に
 * 古い Cookie を残すと、Cookie の有無で判定するページとの間で
 * リダイレクトループが発生するため、必ず削除すること。
 */
export function clearSessionCookies(
  response: import("next/server").NextResponse,
): void {
  response.cookies.set(SESSION_COOKIE, "", {
    ...SESSION_COOKIE_OPTIONS,
    maxAge: 0,
  });
  response.cookies.set(REFRESH_COOKIE, "", {
    ...REFRESH_COOKIE_OPTIONS,
    maxAge: 0,
  });
}

/**
 * bff_refresh Cookie の値からトークンリフレッシュを試み、
 * 新しいアクセストークンと暗号化済みトークンペアを返します。
 *
 * @param refreshCookieValue bff_refresh Cookie の値（未設定時は undefined）
 * @returns リフレッシュ結果、または失敗時は null
 */
const activeRefreshes = new Map<string, Promise<RefreshResult | null>>();

/**
 * bff_refresh Cookie の値からトークンリフレッシュを試み、
 * 新しいアクセストークンと暗号化済みトークンペアを返します。
 *
 * 並行するリクエストが同時にリフレッシュを走らせるのを防ぐため、
 * 同一のトークン値での処理は重複排除（Deduplicate）されます。
 *
 * @param refreshCookieValue bff_refresh Cookie の値（未設定時は undefined）
 * @returns リフレッシュ結果、または失敗時は null
 */
export async function attemptTokenRefresh(
  refreshCookieValue: string | undefined,
): Promise<RefreshResult | null> {
  if (!refreshCookieValue) return null;

  let promise = activeRefreshes.get(refreshCookieValue);
  if (!promise) {
    promise = (async () => {
      const newTokens = await tryRefreshSession(refreshCookieValue);
      if (!newTokens) return null;
      const accessToken = await decryptSession(newTokens.encryptedAccess);
      if (!accessToken) return null;
      return { accessToken, ...newTokens };
    })();

    promise.finally(() => {
      activeRefreshes.delete(refreshCookieValue);
    });

    activeRefreshes.set(refreshCookieValue, promise);
  }

  return promise;
}

/**
 * リフレッシュ後の新しい Cookie を NextResponse にセットします。
 */
export function applyRefreshedCookies(
  response: import("next/server").NextResponse,
  result: RefreshResult,
): void {
  response.cookies.set(
    SESSION_COOKIE,
    result.encryptedAccess,
    SESSION_COOKIE_OPTIONS,
  );
  response.cookies.set(
    REFRESH_COOKIE,
    result.encryptedRefresh,
    REFRESH_COOKIE_OPTIONS,
  );
}

/**
 * bff_refresh Cookie を使って FastAPI /api/auth/refresh を呼び出し、
 * 新しいトークンペアを暗号化して返します。
 *
 * @param refreshCookieValue 現在の bff_refresh Cookie の値
 * @returns 新しい暗号化済みトークンペア、または失敗時は null
 */
export async function tryRefreshSession(
  refreshCookieValue: string,
): Promise<RefreshedTokens | null> {
  const refreshToken = await decryptSession(refreshCookieValue);
  if (!refreshToken) return null;

  try {
    const headerStore = await headers();
    const userAgent = headerStore.get("user-agent");
    const ipAddress =
      headerStore.get("x-forwarded-for") || headerStore.get("x-real-ip");

    const fetchHeaders: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (userAgent) {
      fetchHeaders["User-Agent"] = userAgent;
    }
    if (ipAddress) {
      fetchHeaders["X-Forwarded-For"] = ipAddress;
    }

    const res = await fetch(`${API_BASE}/api/auth/refresh`, {
      method: "POST",
      headers: fetchHeaders,
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return null;

    const data = await res.json();
    const [encryptedAccess, encryptedRefresh] = await Promise.all([
      encryptSession(data.access_token),
      encryptSession(data.refresh_token),
    ]);
    return { encryptedAccess, encryptedRefresh };
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[tryRefreshSession] Failed:", error);
    return null;
  }
}
