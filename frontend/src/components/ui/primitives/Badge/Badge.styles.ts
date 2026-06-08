import { cva } from "@/styled-system/css";

export const badgeStyles = cva({
  base: {
    padding: "2px 10px",
    borderRadius: "full",
    fontSize: "xs",
    fontWeight: 500,
    display: "inline-block",
  },
  variants: {
    variant: {
      requested: {
        background: "badge.requestedBg",
        color: "status.requested",
      },
      processing: {
        background: "badge.processingBg",
        color: "status.processing",
      },
      completed: {
        background: "badge.completedBg",
        color: "status.completed",
      },
      error: {
        background: "badge.errorBg",
        color: "error",
      },
      warning: {
        background: "badge.requestedBg",
        color: "warning",
      },
      default: {
        background: "badge.defaultBg",
        color: "textSecondary",
      },
    },
  },
});
