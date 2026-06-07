import { css } from "@/styled-system/css";

const typingIndicatorStyles = css({
  padding: "4px 20px 0",
  fontSize: "12px",
  color: "textSecondary",
  minHeight: "20px",
});

interface TypingIndicatorProps {
  typingUsers: Set<string>;
}

export function TypingIndicator({ typingUsers }: TypingIndicatorProps) {
  if (typingUsers.size === 0) return null;

  const users = [...typingUsers];
  const text =
    users.length === 1
      ? `${users[0]} is typing...`
      : `${users.join(", ")} are typing...`;

  return <p className={typingIndicatorStyles}>{text}</p>;
}
