"use client";

import { useSessions } from "@/features/auth/hooks/useSessions";
import {
  currentBadgeStyles,
  deviceLineStyles,
  errorMessageStyles,
  metaLineStyles,
  revokeButtonStyles,
  sessionInfoStyles,
  sessionItemStyles,
  sessionListStyles,
  sessionSectionStyles,
  sessionTitleStyles,
  statusMessageStyles,
} from "./SessionList.styles";

function parseUA(ua: string): string {
  const lowercase = ua.toLowerCase();
  let os = "不明なOS";
  let browser = "不明なブラウザ";

  if (lowercase.includes("win")) os = "Windows";
  else if (lowercase.includes("mac")) os = "macOS";
  else if (lowercase.includes("linux")) os = "Linux";
  else if (lowercase.includes("iphone") || lowercase.includes("ipad"))
    os = "iOS";
  else if (lowercase.includes("android")) os = "Android";

  if (lowercase.includes("edg")) browser = "Edge";
  else if (lowercase.includes("chrome") && !lowercase.includes("safari"))
    browser = "Chrome";
  else if (lowercase.includes("safari") && !lowercase.includes("chrome"))
    browser = "Safari";
  else if (lowercase.includes("firefox")) browser = "Firefox";
  else if (lowercase.includes("opr") || lowercase.includes("opera"))
    browser = "Opera";
  else if (lowercase.includes("chrome") && lowercase.includes("safari"))
    browser = "Chrome";

  return `${os} • ${browser}`;
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr;
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${d.getFullYear()}/${pad(d.getMonth() + 1)}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function SessionList() {
  const { sessions, loading, error, revokeSession } = useSessions();

  const handleRevoke = (id: string, ua: string) => {
    const device = parseUA(ua);
    if (window.confirm(`セッション「${device}」を切断しますか？`)) {
      revokeSession(id);
    }
  };

  return (
    <div className={sessionSectionStyles}>
      <p className={sessionTitleStyles}>ログイン中の端末</p>
      {loading && <div className={statusMessageStyles}>読み込み中...</div>}
      {error && <div className={errorMessageStyles}>{error}</div>}
      {!loading && !error && sessions.length === 0 && (
        <div className={statusMessageStyles}>セッションが見つかりません</div>
      )}
      {!loading && !error && sessions.length > 0 && (
        <div className={sessionListStyles}>
          {sessions.map((session) => (
            <div key={session.id} className={sessionItemStyles}>
              <div className={sessionInfoStyles}>
                <div className={deviceLineStyles}>
                  <span>{parseUA(session.user_agent)}</span>
                  {session.is_current && (
                    <span className={currentBadgeStyles}>現在の端末</span>
                  )}
                </div>
                <div className={metaLineStyles}>
                  <span>IP: {session.ip_address}</span>
                  <span>ログイン: {formatDate(session.created_at)}</span>
                </div>
              </div>
              {!session.is_current && (
                <button
                  type="button"
                  onClick={() => handleRevoke(session.id, session.user_agent)}
                  className={revokeButtonStyles}
                >
                  切断
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
