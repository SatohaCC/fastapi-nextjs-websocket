import { css, cva } from "@/styled-system/css";

export const barStyles = css({
  display: "flex",
  alignItems: "center",
  flexWrap: "wrap",
  gap: "8px",
  padding: "8px 24px",
  borderBottom: "1px solid",
  borderBottomColor: "border.default",
  background: "panelBg",
  fontSize: "12px",
  "@media (max-width: 1024px)": {
    padding: "8px 12px",
  },
});

export const labelStyles = css({
  display: "inline-flex",
  alignItems: "center",
  gap: "6px",
  color: "textMuted",
  fontWeight: 500,
  whiteSpace: "nowrap",
});

export const countDotStyles = css({
  width: "7px",
  height: "7px",
  borderRadius: "50%",
  background: "success",
  flexShrink: 0,
});

export const listStyles = css({
  display: "flex",
  flexWrap: "wrap",
  gap: "6px",
  alignItems: "center",
  listStyle: "none",
  margin: 0,
  padding: 0,
});

export const chipStyles = cva({
  base: {
    display: "inline-flex",
    alignItems: "center",
    gap: "4px",
    padding: "2px 10px",
    borderRadius: "full",
    border: "1px solid",
    borderColor: "status.onlineBorder",
    background: "badge.completedBg",
    color: "success",
    fontWeight: 500,
    whiteSpace: "nowrap",
  },
  variants: {
    self: {
      true: {
        borderColor: "border.muted",
        background: "surface.subtle",
        color: "textPrimary",
      },
    },
  },
});

export const emptyStyles = css({
  color: "textMuted",
  fontStyle: "italic",
});
