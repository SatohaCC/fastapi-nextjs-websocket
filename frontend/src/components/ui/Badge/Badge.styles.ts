import { cva } from "@/styled-system/css";

export const badgeStyles = cva({
  base: {
    padding: "2px 12px",
    borderRadius: "99px",
    fontSize: "0.8rem",
    fontWeight: 700,
    display: "inline-block",
  },
  variants: {
    variant: {
      requested: {
        background: "rgba(255, 212, 0, 0.1)",
        color: "status.requested",
      },
      processing: {
        background: "rgba(29, 155, 240, 0.1)",
        color: "status.processing",
      },
      completed: {
        background: "rgba(0, 186, 124, 0.1)",
        color: "status.completed",
      },
      error: {
        background: "rgba(244, 33, 46, 0.1)",
        color: "error",
      },
      warning: {
        background: "rgba(255, 212, 0, 0.1)",
        color: "warning",
      },
      default: {
        background: "rgba(113, 118, 123, 0.1)",
        color: "textSecondary",
      },
    },
  },
});
