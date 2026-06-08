import type { ToastItem } from "@/lib/toast";
import {
  bodyStyles,
  closeStyles,
  descriptionStyles,
  leavingStyles,
  titleStyles,
  toastStyles,
} from "./Toast.styles";

interface ToastProps extends ToastItem {
  onClose: (id: string) => void;
}

export function Toast({
  id,
  title,
  description,
  leaving,
  onClose,
}: ToastProps) {
  return (
    <output
      aria-live="polite"
      className={`${toastStyles} ${leaving ? leavingStyles : ""}`.trim()}
    >
      <div className={bodyStyles}>
        <p className={titleStyles}>{title}</p>
        {description && <p className={descriptionStyles}>{description}</p>}
      </div>
      <button
        className={closeStyles}
        onClick={() => onClose(id)}
        aria-label="閉じる"
        type="button"
      >
        ×
      </button>
    </output>
  );
}
