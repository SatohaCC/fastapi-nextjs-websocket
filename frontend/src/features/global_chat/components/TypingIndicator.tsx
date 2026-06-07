import { typingIndicatorStyles } from "./GlobalChat.styles";

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
