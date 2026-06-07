"use client";

import { Switch as RACSwitch } from "react-aria-components";
import { css } from "@/styled-system/css";

const switchStyles = css({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "12px 16px",
  borderRadius: "8px",
  background: "panelBg",
  border: "1px solid",
  borderColor: "panelBorder",
  cursor: "pointer",
  userSelect: "none",
});

const labelStyles = css({
  fontSize: "15px",
  fontWeight: 500,
  color: "textPrimary",
});

const trackStyles = css({
  position: "relative",
  width: "44px",
  height: "24px",
  borderRadius: "99px",
  background: "#2f3336",
  transition: "background 0.2s",
  display: "inline-block",
  "&[data-selected]": {
    background: "primary",
  },
});

const thumbStyles = css({
  position: "absolute",
  top: "2px",
  left: "2px",
  width: "20px",
  height: "20px",
  borderRadius: "50%",
  background: "white",
  transition: "transform 0.2s",
  "&[data-selected]": {
    transform: "translateX(20px)",
  },
});

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
}

export function Toggle({ checked, onChange, label }: ToggleProps) {
  return (
    <RACSwitch
      isSelected={checked}
      onChange={onChange}
      className={switchStyles}
    >
      {({ isSelected }) => (
        <>
          <span className={labelStyles}>{label}</span>
          <span
            className={trackStyles}
            data-selected={isSelected ? "" : undefined}
          >
            <span
              className={thumbStyles}
              data-selected={isSelected ? "" : undefined}
            />
          </span>
        </>
      )}
    </RACSwitch>
  );
}
