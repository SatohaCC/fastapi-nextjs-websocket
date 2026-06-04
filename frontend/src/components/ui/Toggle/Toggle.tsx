"use client";

import { useId } from "react";
import styles from "./Toggle.module.css";

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
}

export function Toggle({ checked, onChange, label }: ToggleProps) {
  const id = useId();

  return (
    <label htmlFor={id} className={styles.row}>
      <span className={styles.label}>{label}</span>
      <span className={`${styles.track} ${checked ? styles.trackChecked : ""}`}>
        <input
          id={id}
          type="checkbox"
          role="switch"
          aria-checked={checked}
          className={styles.input}
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <span
          className={`${styles.thumb} ${checked ? styles.thumbChecked : ""}`}
        />
      </span>
    </label>
  );
}
