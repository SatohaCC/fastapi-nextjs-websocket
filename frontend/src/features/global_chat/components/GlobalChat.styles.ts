import { css } from "@/styled-system/css";

export const inputFormStyles = css({
  padding: "12px 16px",
  display: "flex",
  gap: "8px",
  alignItems: "center",
});

export const inputWrapperStyles = css({
  position: "relative",
  flex: 1,
  minWidth: 0,
});

export const headerTitleStyles = css({
  fontSize: "15px",
  fontWeight: 500,
  color: "textPrimary",
  letterSpacing: "0.01em",
});

export const headerSubtitleStyles = css({
  fontSize: "12px",
  color: "textSecondary",
  marginTop: "2px",
});
