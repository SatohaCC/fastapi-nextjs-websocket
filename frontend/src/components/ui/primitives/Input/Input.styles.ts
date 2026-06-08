import { css } from "@/styled-system/css";

export const inputStyles = css({
  background: "panelBg",
  border: "1px solid",
  borderColor: "panelBorder",
  color: "textPrimary",
  padding: "0 16px",
  height: "42px",
  borderRadius: "control",
  width: "100%",
  fontSize: "14px",
  outline: "none",
  transition: "border-color 0.2s, box-shadow 0.2s",
  _focus: {
    borderColor: "primary",
    outline: "none",
    boxShadow: "focus",
  },
  _placeholder: {
    color: "textSecondary",
  },
});

export const selectStyles = css({
  background: "panelBg",
  border: "1px solid",
  borderColor: "panelBorder",
  color: "textPrimary",
  padding: "0 40px 0 16px",
  height: "42px",
  borderRadius: "control",
  width: "100%",
  fontSize: "14px",
  outline: "none",
  transition: "border-color 0.2s, box-shadow 0.2s",
  appearance: "none",
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%235F6368' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
  backgroundRepeat: "no-repeat",
  backgroundPosition: "right 13px center",
  _focus: {
    borderColor: "primary",
    outline: "none",
    boxShadow: "focus",
  },
});
