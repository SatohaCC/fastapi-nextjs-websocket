import { css } from "@/styled-system/css";

export const panelStyles = css({
  gridRow: "span 3",
  display: "grid",
  gridTemplateRows: "subgrid",
  "@media (max-width: 1024px)": {
    gridRow: "unset",
    display: "flex",
    flexDirection: "column",
  },
});

export const titleStyles = css({
  fontSize: "15px",
  fontWeight: 500,
  color: "textPrimary",
  letterSpacing: "0.01em",
});

export const subtitleStyles = css({
  fontSize: "12px",
  color: "textSecondary",
  marginTop: "2px",
});

export const messagesAreaStyles = css({
  padding: "16px 20px 16px 20px",
  display: "flex",
  flexDirection: "column",
  gap: "14px",
  overflowY: "auto",
  overflowX: "hidden",
  minHeight: 0,
  background: "bg",
  scrollbarGutter: "stable",
});

export const formWrapperStyles = css({
  borderTop: "1px solid",
  borderTopColor: "border.divider",
  display: "flex",
  flexDirection: "column",
  justifyContent: "flex-end",
  background: "panelBg",
});

export const messageWrapperStyles = css({
  maxWidth: "72%",
  display: "flex",
  flexDirection: "column",
});

export const messageWrapperMeStyles = css({
  alignSelf: "flex-end",
  alignItems: "flex-end",
  marginRight: "4px",
});

export const messageWrapperOtherStyles = css({
  alignSelf: "flex-start",
  alignItems: "flex-start",
  marginLeft: "4px",
});

export const senderNameStyles = css({
  fontSize: "13px",
  fontWeight: 500,
  marginBottom: "4px",
  marginLeft: "8px",
  color: "textSecondary",
});

export const bubbleStyles = css({
  padding: "10px 16px",
  fontSize: "14px",
  lineHeight: 1.55,
  wordBreak: "break-word",
  minWidth: "48px",
  minHeight: "40px",
});

export const bubbleMeStyles = css({
  borderTopLeftRadius: "bubble",
  borderTopRightRadius: "bubble",
  borderBottomLeftRadius: "bubble",
  borderBottomRightRadius: "tag",
  background: "primary",
  color: "white!",
  boxShadow: "bubble",
});

export const bubbleOtherStyles = css({
  borderTopLeftRadius: "bubble",
  borderTopRightRadius: "bubble",
  borderBottomLeftRadius: "tag",
  borderBottomRightRadius: "bubble",
  background: "panelBg",
  border: "1px solid",
  borderColor: "border.default",
  color: "textPrimary",
  boxShadow: "subtle",
});

export const timestampStyles = css({
  fontSize: "11px",
  color: "textMuted",
  marginTop: "4px",
});

export const timestampMeStyles = css({
  marginRight: "8px",
});

export const timestampOtherStyles = css({
  marginLeft: "8px",
});

export const inputFormStyles = css({
  padding: "12px 16px",
  display: "flex",
  gap: "8px",
  alignItems: "center",
});

export const textInputStyles = css({
  borderRadius: "control!",
  background: "panelBg",
  border: "1px solid",
  borderColor: "panelBorder!",
  flex: 1,
  height: "42px",
  color: "textPrimary",
  fontSize: "14px!",
  padding: "0 16px!",
  _focus: {
    borderColor: "primary!",
    boxShadow: "focus!",
    outline: "none",
  },
  _placeholder: {
    color: "textMuted",
  },
});

export const sendButtonStyles = css({
  padding: "0 20px",
  borderRadius: "control!",
  fontWeight: 500,
  height: "42px",
  fontSize: "14px",
  minWidth: "64px",
});

export const messagePendingStyles = css({
  opacity: 0.5,
});

export const inputWrapperStyles = css({
  position: "relative",
  flex: 1,
  minWidth: 0,
});

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

// Mention of another user — inside white bubble
export const mentionStyles = css({
  background: "mention.bg",
  color: "primary",
  fontWeight: 500,
  borderRadius: "tag",
  padding: "1px 4px",
});

// Mention of another user — inside blue bubble (my message)
export const mentionInMeBubbleStyles = css({
  background: "mention.inBubbleBg",
  color: "white",
  fontWeight: 500,
  borderRadius: "tag",
  padding: "1px 4px",
});

// Mention of myself — inside white bubble
export const mentionMeStyles = css({
  background: "mention.meBg",
  color: "warning",
  fontWeight: 500,
  borderRadius: "tag",
  padding: "1px 4px",
});

// Mention of myself — inside blue bubble
export const mentionMeInMeBubbleStyles = css({
  background: "mention.inBubbleBg",
  color: "mention.meInBubbleColor",
  fontWeight: 500,
  borderRadius: "tag",
  padding: "1px 4px",
});

export const typingIndicatorStyles = css({
  padding: "4px 16px 0",
  fontSize: "12px",
  color: "textMuted",
  minHeight: "20px",
});
