import "server-only";
import crypto from "node:crypto";

const ALGORITHM = "aes-256-gcm";
const IV_LENGTH = 12;
const SECRET_KEY =
  process.env.BFF_SECRET || "dev-secret-key-32-bytes-long-1234567";

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
