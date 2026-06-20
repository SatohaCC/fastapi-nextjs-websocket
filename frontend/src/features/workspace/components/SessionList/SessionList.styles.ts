import { css } from "@/styled-system/css";

export const sessionSectionStyles = css({
  borderTop: "1px solid",
  borderColor: "border.default",
  marginTop: "12px",
  paddingTop: "12px",
});

export const sessionTitleStyles = css({
  fontSize: "2xs",
  fontWeight: 600,
  color: "textSecondary",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  marginBottom: "12px",
  paddingLeft: "4px",
});

export const sessionListStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "8px",
  maxHeight: "240px",
  overflowY: "auto",
  paddingRight: "4px",
  "&::-webkit-scrollbar": {
    width: "4px",
  },
  "&::-webkit-scrollbar-track": {
    background: "transparent",
  },
  "&::-webkit-scrollbar-thumb": {
    background: "border.default",
    borderRadius: "full",
  },
});

export const sessionItemStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "8px",
  borderRadius: "control",
  background: "surface.subtle",
  border: "1px solid transparent",
  transition: "all 0.15s ease",
  _hover: {
    background: "surface.active",
    borderColor: "border.overlay",
  },
});

export const sessionInfoStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "2px",
});

export const deviceLineStyles = css({
  fontSize: "sm",
  fontWeight: 500,
  color: "textPrimary",
  display: "flex",
  alignItems: "center",
  gap: "6px",
});

export const currentBadgeStyles = css({
  fontSize: "2xs",
  fontWeight: 600,
  color: "success",
  background: "badge.completedBg",
  padding: "2px 6px",
  borderRadius: "full",
  border: "1px solid",
  borderColor: "status.onlineBorder",
  whiteSpace: "nowrap",
});

export const metaLineStyles = css({
  fontSize: "xs",
  color: "textMuted",
  display: "flex",
  alignItems: "center",
  gap: "8px",
  flexWrap: "wrap",
});

export const revokeButtonStyles = css({
  background: "transparent",
  border: "1px solid",
  borderColor: "transparent",
  color: "error",
  padding: "4px 8px",
  fontSize: "xs",
  borderRadius: "control",
  fontWeight: 500,
  cursor: "pointer",
  transition: "all 0.15s ease",
  whiteSpace: "nowrap",
  _hover: {
    background: "badge.errorBg",
    borderColor: "error",
  },
  _active: {
    transform: "scale(0.96)",
  },
});

export const statusMessageStyles = css({
  fontSize: "xs",
  color: "textMuted",
  padding: "8px",
  textAlign: "center",
});

export const errorMessageStyles = css({
  fontSize: "xs",
  color: "error",
  padding: "8px",
  textAlign: "center",
});
