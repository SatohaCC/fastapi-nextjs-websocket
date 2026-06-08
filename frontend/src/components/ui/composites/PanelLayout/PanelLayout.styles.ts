import { css, cva } from "@/styled-system/css";

export const containerStyles = css({
  gridRow: "span 3",
  display: "grid",
  gridTemplateRows: "subgrid",
  "@media (max-width: 1024px)": {
    gridRow: "unset",
    display: "flex",
    flexDirection: "column",
  },
});

export const contentStyles = cva({
  base: {
    overflowY: "auto",
    minHeight: 0,
    display: "flex",
    flexDirection: "column",
    background: "bg",
    "@media (max-width: 1024px)": {
      flex: 1,
    },
  },
  variants: {
    padding: {
      none: {
        padding: 0,
      },
      normal: {
        padding: "16px 20px",
        gap: "14px",
      },
    },
  },
  defaultVariants: {
    padding: "none",
  },
});

export const formWrapperStyles = css({
  borderTop: "1px solid",
  borderColor: "border.divider",
  display: "flex",
  flexDirection: "column",
  justifyContent: "flex-end",
});
