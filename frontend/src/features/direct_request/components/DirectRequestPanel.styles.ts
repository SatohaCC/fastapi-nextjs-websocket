import { css } from "@/styled-system/css";

export const requestFormStyles = css({
  padding: "12px 16px",
  display: "flex",
  gap: "8px",
  alignItems: "center",
});

export const inputGroupStyles = css({
  display: "flex",
  flex: 1,
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
  fontSize: "lg",
  fontWeight: 500,
  color: "textPrimary",
  letterSpacing: "0.01em",
});

export const headerSubtitleStyles = css({
  fontSize: "xs",
  color: "textSecondary",
  marginTop: "2px",
});
