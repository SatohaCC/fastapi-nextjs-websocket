import { css } from "@/styled-system/css";

export const settingsPanelStyles = css({
  position: "absolute",
  top: "calc(100% + 8px)",
  right: 0,
  background: "panelBg",
  border: "1px solid",
  borderColor: "border.default",
  borderRadius: "panel",
  padding: "16px",
  minWidth: "280px",
  zIndex: 100,
  boxShadow: "panel",
  animation: "fadeIn 0.15s ease-out",
});

export const settingsTitleStyles = css({
  fontSize: "11px",
  fontWeight: 600,
  color: "textSecondary",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  marginBottom: "12px",
  paddingLeft: "4px",
});

export const settingsListStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "4px",
});
