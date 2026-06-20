"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Input } from "@/components/ui/primitives";
import { useAccountSettings } from "@/features/auth/hooks/useAccountSettings";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { WorkspaceLoading } from "@/features/workspace/components/WorkspaceLoading";
import { toast } from "@/lib/toast";
import {
  backButtonStyles,
  errorTextStyles,
  formRowStyles,
  formSectionStyles,
  inlineButtonStyles,
  settingsListStyles,
  settingsPageWrapperStyles,
  settingsPanelStyles,
  settingsTitleStyles,
  statusTextStyles,
  successTextStyles,
} from "./NotificationSettings.styles";

export function ChangePasswordForm() {
  const router = useRouter();
  const { isAuthenticated, username, isSessionLoaded, clearSession } =
    useAuth();
  const {
    currentPassword,
    setCurrentPassword,
    newPassword,
    setNewPassword,
    passwordError,
    passwordSuccess,
    passwordLoading,
    handleChangePassword,
  } = useAccountSettings();

  useEffect(() => {
    if (isSessionLoaded && (!isAuthenticated || !username)) {
      router.replace("/");
    }
  }, [isSessionLoaded, isAuthenticated, username, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    const success = await handleChangePassword(e);
    if (success) {
      toast.message("パスワードを変更しました。再ログインしてください。");
      await clearSession();
      router.push("/");
    }
  };

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
            パスワードの変更
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
            <p className={settingsTitleStyles}>認証情報のセキュリティ</p>
            <form onSubmit={handleSubmit} className={formSectionStyles}>
              <div className={settingsListStyles} style={{ gap: "12px" }}>
                <Input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="現在のパスワード"
                  required
                  disabled={passwordLoading}
                />
                <div className={formRowStyles}>
                  <Input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="新しいパスワード"
                    required
                    disabled={passwordLoading}
                  />
                  <button
                    type="submit"
                    className={inlineButtonStyles}
                    disabled={passwordLoading}
                  >
                    {passwordLoading ? "変更中" : "変更"}
                  </button>
                </div>
              </div>
              {passwordError && (
                <output className={`${statusTextStyles} ${errorTextStyles}`}>
                  {passwordError}
                </output>
              )}
              {passwordSuccess && (
                <output className={`${statusTextStyles} ${successTextStyles}`}>
                  {passwordSuccess}
                </output>
              )}
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}
