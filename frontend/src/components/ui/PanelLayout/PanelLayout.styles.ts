import { css } from "@/styled-system/css";

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

export const contentStyles = css({
  overflowY: "auto",
  minHeight: 0,
  "@media (max-width: 1024px)": {
    flex: 1,
  },
});

export const formWrapperStyles = css({
  borderTop: "1px solid",
  borderColor: "panelBorder",
  display: "flex",
  flexDirection: "column",
  justifyContent: "flex-end",
});
