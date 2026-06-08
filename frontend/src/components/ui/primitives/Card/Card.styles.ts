import { css } from "@/styled-system/css";

export const cardStyles = css({
  background: "panelBg",
  border: "1px solid",
  borderColor: "border.default",
  borderRadius: "panel",
  overflow: "hidden",
  boxShadow: "card",
});

export const hoverableStyles = css({
  transition: "box-shadow 0.2s",
  _hover: {
    boxShadow: "cardHover",
  },
});

export const headerStyles = css({
  padding: "16px 20px",
  borderBottom: "1px solid",
  borderBottomColor: "border.divider",
  background: "panelBg",
});

export const contentStyles = css({
  padding: "20px",
});
