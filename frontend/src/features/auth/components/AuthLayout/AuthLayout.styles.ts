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

export const successBoxStyles = css({
  padding: "12px 16px",
  background: "rgba(16, 185, 129, 0.1)",
  color: "rgba(16, 185, 129, 1)",
  borderRadius: "panel",
  fontSize: "13px",
  textAlign: "center",
  border: "1px solid",
  borderColor: "rgba(16, 185, 129, 0.2)",
  fontWeight: 500,
});
