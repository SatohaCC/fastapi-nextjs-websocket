import { css } from "@/styled-system/css";

export const containerStyles = css({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  height: "100vh",
  background: "bg",
  overflow: "hidden",
  padding: "20px",
});

export const formStyles = css({
  padding: "48px 48px 40px",
  width: "100%",
  maxWidth: "480px",
  display: "flex",
  flexDirection: "column",
  gap: "24px",
  background: "panelBg",
  borderRadius: "panel",
  border: "1px solid",
  borderColor: "border.default",
  boxShadow: "modal",
});

export const headerStyles = css({
  textAlign: "center",
});

export const logoStyles = css({
  fontSize: "26px",
  fontWeight: 500,
  color: "textPrimary",
  letterSpacing: "-0.01em",
});

export const subtitleStyles = css({
  fontSize: "14px",
  color: "textSecondary",
  marginTop: "10px",
  lineHeight: 1.6,
});

export const accountsStyles = css({
  border: "1px solid",
  borderColor: "border.default",
  borderRadius: "control",
  background: "panelBg",
  overflow: "hidden",
  boxShadow: "subtle",
});

export const accountsLabelStyles = css({
  fontSize: "11px",
  fontWeight: 500,
  color: "textMuted",
  padding: "10px 16px",
  borderBottom: "1px solid",
  borderBottomColor: "border.divider",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  background: "bg",
});

export const accountItemStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "14px 18px",
  width: "100%",
  background: "transparent",
  border: "none",
  borderBottom: "1px solid",
  borderBottomColor: "border.divider",
  color: "textPrimary",
  cursor: "pointer",
  fontSize: "14px",
  transition: "background 0.15s ease",
  textAlign: "left",
  _last: {
    borderBottom: "none",
  },
  _hover: {
    background: "bg",
  },
  _focusVisible: {
    outlineWidth: "2px",
    outlineStyle: "solid",
    outlineColor: "primary",
    outlineOffset: "-2px",
    background: "bg",
  },
});

export const accountItemActiveStyles = css({
  background: "surface.active!",
  borderLeftWidth: "3px",
  borderLeftStyle: "solid",
  borderLeftColor: "primary",
  paddingLeft: "15px",
  _hover: {
    background: "surface.active!",
  },
});

export const accountNameStyles = css({
  fontWeight: 500,
  color: "textPrimary",
  fontSize: "14px",
});

export const accountPasswordStyles = css({
  fontSize: "12px",
  color: "textMuted",
  fontFamily: "monospace",
  letterSpacing: "0.02em",
});

export const errorBoxStyles = css({
  padding: "12px 16px",
  background: "badge.errorBg",
  color: "error",
  borderRadius: "panel",
  fontSize: "13px",
  textAlign: "center",
  border: "1px solid",
  borderColor: "border.errorOverlay",
  fontWeight: 500,
});

export const fieldGroupStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "16px",
});

export const submitButtonStyles = css({
  padding: "14px",
  fontSize: "15px",
  fontWeight: 500,
  width: "100%",
  borderRadius: "control!",
  letterSpacing: "0.01em",
  _active: {
    transform: "scale(0.99)",
  },
});
