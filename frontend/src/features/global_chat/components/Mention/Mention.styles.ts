import { css } from "@/styled-system/css";

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
