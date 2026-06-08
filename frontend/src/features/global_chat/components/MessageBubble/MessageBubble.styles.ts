import { css } from "@/styled-system/css";

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

export const messagePendingStyles = css({
  opacity: 0.5,
});
