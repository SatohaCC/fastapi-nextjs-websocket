import { css } from "@/styled-system/css";

export const containerStyles = css({
  height: "100vh",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: "24px",
  padding: "20px",
  textAlign: "center",
  background: "bg",
});

export const headingStyles = css({
  fontSize: "5xl",
  fontWeight: 900,
  color: "error",
  letterSpacing: "-0.05em",
});

export const messageStyles = css({
  color: "textSecondary",
  maxWidth: "400px",
});

export const detailBoxStyles = css({
  padding: "16px",
  background: "badge.errorBg",
  border: "1px solid",
  borderColor: "border.errorOverlay",
  borderRadius: "panel",
  fontFamily: "monospace",
  fontSize: "xs",
  color: "error",
});
