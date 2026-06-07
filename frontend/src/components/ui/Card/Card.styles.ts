import { css } from "@/styled-system/css";

export const cardStyles = css({
  background: "rgba(18, 18, 23, 0.7)",
  backdropFilter: "blur(12px) saturate(180%)",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: "16px",
  overflow: "hidden",
  boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
});

export const hoverableStyles = css({
  transition: "background 0.2s",
  _hover: {
    background: "rgba(255, 255, 255, 0.03)",
  },
});

export const headerStyles = css({
  padding: "16px 20px",
  borderBottom: "1px solid",
  borderColor: "panelBorder",
});

export const contentStyles = css({
  padding: "20px",
});
