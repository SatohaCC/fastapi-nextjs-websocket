import { css, cva } from "@/styled-system/css";

export const headerStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "0 32px",
  height: "64px",
  borderBottom: "1px solid",
  borderBottomColor: "border.default",
  background: "panelBg",
  position: "sticky",
  top: 0,
  zIndex: 10,
  boxShadow: "header",
  "@media (max-width: 1024px)": {
    flexDirection: "column",
    height: "auto",
    padding: "12px 20px",
    gap: "12px",
    alignItems: "flex-start",
  },
});

export const brandGroupStyles = css({
  display: "flex",
  alignItems: "center",
  gap: "16px",
});

export const logoStyles = css({
  fontSize: "18px",
  fontWeight: 500,
  color: "textPrimary",
  letterSpacing: "0",
});

export const statusIndicatorStyles = cva({
  base: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    fontSize: "12px",
    padding: "4px 12px",
    borderRadius: "full",
    border: "1px solid",
    fontWeight: 500,
    whiteSpace: "nowrap",
    flexShrink: 0,
  },
  variants: {
    status: {
      online: {
        background: "badge.completedBg",
        borderColor: "status.onlineBorder",
        color: "success",
      },
      offline: {
        background: "badge.errorBg",
        borderColor: "error",
        color: "error",
      },
      connecting: {
        background: "badge.requestedBg",
        borderColor: "warning",
        color: "warning",
      },
    },
  },
  defaultVariants: {
    status: "connecting",
  },
});

export const statusDotStyles = cva({
  base: {
    width: "7px",
    height: "7px",
    borderRadius: "50%",
    flexShrink: 0,
  },
  variants: {
    status: {
      online: {
        background: "success",
      },
      offline: {
        background: "error",
      },
      connecting: {
        background: "warning",
      },
    },
  },
  defaultVariants: {
    status: "connecting",
  },
});

export const systemInfoStyles = css({
  fontSize: "12px",
  color: "textMuted",
  marginLeft: "4px",
  fontFamily: "monospace",
  letterSpacing: "0.03em",
  display: "flex",
  gap: "10px",
  alignItems: "center",
});

export const userGroupStyles = css({
  display: "flex",
  alignItems: "center",
  gap: "16px",
  "@media (max-width: 1024px)": {
    width: "100%",
    justifyContent: "space-between",
  },
});

export const userInfoStyles = css({
  textAlign: "right",
  display: "flex",
  flexDirection: "column",
  gap: "1px",
});

export const usernameStyles = css({
  fontSize: "14px",
  color: "textPrimary",
  fontWeight: 500,
});

export const handleStyles = css({
  fontSize: "12px",
  color: "textMuted",
});

export const gearButtonStyles = css({
  background: "transparent",
  border: "1px solid",
  borderColor: "border.default",
  cursor: "pointer",
  fontSize: "15px",
  color: "textSecondary",
  padding: "7px 9px",
  borderRadius: "50%",
  lineHeight: 1,
  transition: "all 0.15s ease",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  _hover: {
    color: "textPrimary",
    background: "surface.subtle",
    borderColor: "border.muted",
  },
});

export const settingsWrapperStyles = css({
  position: "relative",
});

export const logoutButtonStyles = css({
  background: "panelBg",
  border: "1px solid",
  borderColor: "panelBorder",
  color: "textSecondary",
  padding: "8px 16px",
  fontSize: "sm",
  borderRadius: "control",
  fontWeight: 500,
  cursor: "pointer",
  transition: "all 0.2s ease",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  outline: "none",
  _hover: {
    color: "error",
    background: "badge.errorBg",
    borderColor: "error",
  },
  _active: {
    transform: "scale(0.98)",
  },
  "&[data-focus-visible]": {
    outlineWidth: "3px",
    outlineStyle: "solid",
    outlineColor: "error",
    outlineOffset: "3px",
  },
});
