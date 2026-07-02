"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { Button } from "@/components/ui/primitives";
import { useNotificationSettings } from "@/features/common/notifications/useNotificationSettings";
import { NotificationSettings } from "@/features/workspace/components/NotificationSettings/NotificationSettings";
import {
  backButtonStyles,
  settingsHeaderStyles,
  settingsPageTitleStyles,
  settingsPageWrapperStyles,
} from "@/features/workspace/components/NotificationSettings/NotificationSettings.styles";
import { requestBrowserNotificationPermission } from "@/lib/browserNotification";
import type { NotificationSettings as Settings } from "@/lib/notificationSettings";
import { toast } from "@/lib/toast";
import { css } from "@/styled-system/css";

const containerStyles = css({
  padding: "20px 0",
  maxWidth: "600px",
  width: "100%",
  margin: "0 auto",
});

export default function SettingsPage() {
  const router = useRouter();
  const { settings, updateSetting } = useNotificationSettings();

  const handleUpdateSetting = useCallback(
    (key: keyof Settings, value: boolean) => {
      if (key === "browserNotification" && value) {
        requestBrowserNotificationPermission().then((granted) => {
          if (granted) {
            updateSetting("browserNotification", true);
          } else {
            toast.message("ブラウザ通知を有効にできません", {
              description: "ブラウザの設定で通知を許可してください。",
            });
          }
        });
        return;
      }
      updateSetting(key, value);
    },
    [updateSetting],
  );

  return (
    <div className={settingsPageWrapperStyles}>
      <div className={containerStyles}>
        <div className={settingsHeaderStyles}>
          <h2 className={settingsPageTitleStyles}>アカウント・通知設定</h2>
          <Button
            variant="unstyled"
            size="none"
            onPress={() => router.push("/workspace")}
            className={backButtonStyles}
          >
            チャットに戻る
          </Button>
        </div>
        <NotificationSettings
          settings={settings}
          onUpdate={handleUpdateSetting}
        />
      </div>
    </div>
  );
}
