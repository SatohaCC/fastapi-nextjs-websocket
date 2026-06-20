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
  readOnlyFieldStyles,
  sectionTitleStyles,
  settingsPageWrapperStyles,
  settingsPanelStyles,
  settingsTitleStyles,
  statusTextStyles,
  successTextStyles,
} from "./NotificationSettings.styles";

export function ChangeUsernameForm() {
  const router = useRouter();
  const { isAuthenticated, userid, username, isSessionLoaded } = useAuth();
  const {
    newUsername,
    setNewUsername,
    profileError,
    profileSuccess,
    profileLoading,
    handleUpdateUsername,
  } = useAccountSettings();

  useEffect(() => {
    if (isSessionLoaded && (!isAuthenticated || !userid)) {
      router.replace("/");
    }
  }, [isSessionLoaded, isAuthenticated, userid, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    const success = await handleUpdateUsername(e);
    if (success) {
      toast.message("表示名を変更しました。");
      router.push("/settings");
    }
  };

  if (!isSessionLoaded || !userid) {
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
            表示名の変更
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
            <p className={settingsTitleStyles}>ユーザー情報の編集</p>
            <form onSubmit={handleSubmit} className={formSectionStyles}>
              <div>
                <span className={sectionTitleStyles}>ユーザーID (@handle)</span>
                <div className={readOnlyFieldStyles}>@{userid}</div>
              </div>

              <div>
                <span className={sectionTitleStyles}>現在の表示名</span>
                <div className={readOnlyFieldStyles}>{username}</div>
              </div>

              <div>
                <span className={sectionTitleStyles}>新しい表示名</span>
                <div className={formRowStyles}>
                  <Input
                    type="text"
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    placeholder="新しい表示名"
                    required
                    disabled={profileLoading}
                  />
                  <button
                    type="submit"
                    className={inlineButtonStyles}
                    disabled={profileLoading}
                  >
                    {profileLoading ? "保存中" : "変更"}
                  </button>
                </div>
              </div>

              {profileError && (
                <output className={`${statusTextStyles} ${errorTextStyles}`}>
                  {profileError}
                </output>
              )}
              {profileSuccess && (
                <output className={`${statusTextStyles} ${successTextStyles}`}>
                  {profileSuccess}
                </output>
              )}
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}
