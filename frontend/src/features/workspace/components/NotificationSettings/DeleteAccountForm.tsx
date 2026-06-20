"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAccountSettings } from "@/features/auth/hooks/useAccountSettings";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { WorkspaceLoading } from "@/features/workspace/components/WorkspaceLoading";
import {
  backButtonStyles,
  dangerButtonStyles,
  errorTextStyles,
  formSectionStyles,
  settingsPageWrapperStyles,
  settingsPanelStyles,
  settingsTitleStyles,
  statusTextStyles,
} from "./NotificationSettings.styles";

export function DeleteAccountForm() {
  const router = useRouter();
  const { isAuthenticated, username, isSessionLoaded } = useAuth();
  const { deleteError, deleteLoading, handleDeleteAccount } =
    useAccountSettings();

  useEffect(() => {
    if (isSessionLoaded && (!isAuthenticated || !username)) {
      router.replace("/");
    }
  }, [isSessionLoaded, isAuthenticated, username, router]);

  if (!isSessionLoaded || !username) {
    return <WorkspaceLoading />;
  }

  return (
    <div className={settingsPageWrapperStyles}>
      <div
        style={{
          padding: "20px 0",
          maxWidth: "600px",
          width: "100%",
          margin: "0 auto",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px",
          }}
        >
          <h2 style={{ fontSize: "1.5rem", fontWeight: "bold" }}>
            アカウントの削除
          </h2>
          <button
            type="button"
            onClick={() => router.push("/settings")}
            className={backButtonStyles}
          >
            設定に戻る
          </button>
        </div>
        <main
          style={{ width: "100%", display: "flex", justifyContent: "center" }}
        >
          <div className={settingsPanelStyles}>
            <p
              className={settingsTitleStyles}
              style={{ color: "rgb(239, 68, 68)" }}
            >
              危険ゾーン - 退会処理
            </p>
            <div className={formSectionStyles}>
              <p
                style={{
                  fontSize: "13px",
                  color: "textSecondary",
                  lineHeight: 1.6,
                  marginBottom: "12px",
                }}
              >
                退会すると、送信したメッセージ、ダイレクトリクエスト履歴、タスクを含むすべてのアカウントデータが物理的かつ永久に削除されます。この操作は取り消すことができません。
              </p>
              <button
                type="button"
                onClick={handleDeleteAccount}
                className={dangerButtonStyles}
                disabled={deleteLoading}
              >
                {deleteLoading ? "処理中..." : "退会する (アカウント削除)"}
              </button>
              {deleteError && (
                <output className={`${statusTextStyles} ${errorTextStyles}`}>
                  {deleteError}
                </output>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
