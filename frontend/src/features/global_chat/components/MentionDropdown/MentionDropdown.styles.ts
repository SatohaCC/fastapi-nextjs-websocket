import { css } from "@/styled-system/css";

export const mentionDropdownStyles = css({
  position: "absolute",
  bottom: "calc(100% + 8px)",
  left: 0,
  right: 0,
  background: "panelBg",
  border: "1px solid",
  borderColor: "border.default",
  borderRadius: "panel",
  listStyle: "none",
  margin: 0,
  padding: "6px",
  zIndex: 10,
  boxShadow: "dropdown",
});

export const mentionItemStyles = css({
  display: "flex",
  alignItems: "center",
  gap: "10px",
  width: "100%",
  padding: "8px 10px",
  fontSize: "14px",
  borderRadius: "control",
  cursor: "pointer",
  color: "textPrimary",
  background: "transparent",
  border: "none",
  textAlign: "left",
  transition: "background 0.12s",
  _hover: {
    background: "surface.subtle",
  },
  _focusVisible: {
    background: "surface.active",
    outline: "none",
  },
});

export const mentionItemFocusedStyles = css({
  background: "surface.active!",
});

export const mentionAvatarStyles = css({
  flexShrink: 0,
  width: "32px",
  height: "32px",
  borderRadius: "50%",
  background: "primary",
  color: "white",
  fontSize: "13px",
  fontWeight: 500,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  textTransform: "uppercase",
});

export const mentionUserInfoStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "1px",
});

export const mentionUsernameStyles = css({
  fontSize: "14px",
  fontWeight: 500,
  color: "textPrimary",
  lineHeight: 1.3,
});

export const mentionHandleStyles = css({
  fontSize: "12px",
  color: "textMuted",
  lineHeight: 1.3,
});
