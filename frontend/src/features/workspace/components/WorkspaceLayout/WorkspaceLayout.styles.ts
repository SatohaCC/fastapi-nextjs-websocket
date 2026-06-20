import { css } from "@/styled-system/css";

export const containerStyles = css({
  height: "100%",
  display: "flex",
  flexDirection: "column",
  background: "workspaceBg",
  "@media (max-width: 1024px)": {
    height: "auto",
    minHeight: "calc(100vh - 64px)",
  },
});

export const errorToastStyles = css({
  padding: "10px 20px",
  background: "badge.errorBg",
  color: "error",
  fontSize: "13px",
  textAlign: "center",
  borderBottom: "1px solid",
  borderBottomColor: "border.errorOverlay",
  fontWeight: 500,
});

export const mainStyles = css({
  flex: 1,
  display: "grid",
  gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)",
  gridTemplateRows: "auto 1fr auto",
  columnGap: "16px",
  rowGap: 0,
  minHeight: 0,
  padding: "20px 24px",
  "@media (max-width: 1024px)": {
    gridTemplateColumns: "1fr",
    gridTemplateRows: "unset",
    gap: "16px",
    overflowY: "auto",
    padding: "12px",
  },
});
