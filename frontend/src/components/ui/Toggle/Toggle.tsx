"use client";

import { Switch as RACSwitch } from "react-aria-components";
import { switchStyles, labelStyles, trackStyles, thumbStyles } from "./Toggle.styles";

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
