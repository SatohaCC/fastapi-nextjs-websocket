import {
  mentionInMeBubbleStyles,
  mentionMeInMeBubbleStyles,
  mentionMeStyles,
  mentionStyles,
} from "./GlobalChat.styles";

interface MentionTextProps {
  text: string;
  currentUser: string;
  isInMeBubble?: boolean;
}

export function MentionText({
  text,
  currentUser,
  isInMeBubble = false,
}: MentionTextProps) {
  const parts = text.split(/(@\w+)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (!part.startsWith("@")) {
          // biome-ignore lint/suspicious/noArrayIndexKey: split result is positional by nature
          return <span key={i}>{part}</span>;
        }
        const username = part.slice(1);
        const isMe = username === currentUser;

        let className: string;
        if (isInMeBubble) {
          className = isMe
            ? mentionMeInMeBubbleStyles
            : mentionInMeBubbleStyles;
        } else {
          className = isMe ? mentionMeStyles : mentionStyles;
        }

        return (
          // biome-ignore lint/suspicious/noArrayIndexKey: split result is positional by nature
          <mark key={i} className={className}>
            {part}
          </mark>
        );
      })}
    </>
  );
}
