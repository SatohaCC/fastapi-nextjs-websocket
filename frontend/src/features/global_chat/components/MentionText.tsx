import styles from "./GlobalChat.module.css";

interface MentionTextProps {
  text: string;
  currentUser: string;
}

export function MentionText({ text, currentUser }: MentionTextProps) {
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
        return (
          // biome-ignore lint/suspicious/noArrayIndexKey: split result is positional by nature
          <mark key={i} className={isMe ? styles.mentionMe : styles.mention}>
            {part}
          </mark>
        );
      })}
    </>
  );
}
