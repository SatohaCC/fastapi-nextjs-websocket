import { css } from "@/styled-system/css";

export const requestFormStyles = css({
  padding: "12px 16px",
  background: "panelBg",
});

export const formGridStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "10px",
});

export const inputGroupStyles = css({
  display: "flex",
  gap: "8px",
  overflow: "hidden",
  minWidth: "0",
  "& select": {
    flex: "0 0 auto",
    width: "160px!",
  },
  "& input": {
    flex: "1",
    minWidth: "0",
    width: "auto!",
  },
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
