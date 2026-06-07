import { css } from "@/styled-system/css";

const mentionStyles = css({
  background: "transparent",
  color: "primary",
  fontWeight: 700,
  // 自分のチャットバブル上ではコントラスト調整
  ".bubbleMe &": {
    background: "rgba(255, 255, 255, 0.22)",
    color: "#ffffff",
    borderRadius: "3px",
    padding: "0 3px",
  },
});

const mentionMeStyles = css({
  background: "rgba(251, 191, 36, 0.22)",
  color: "#fbbf24",
  fontWeight: 700,
  borderRadius: "3px",
  padding: "0 3px",
  boxShadow: "0 0 0 1px rgba(251, 191, 36, 0.35)",
  // 自分のチャットバブル上ではコントラスト調整
  ".bubbleMe &": {
    background: "rgba(251, 191, 36, 0.35)",
    color: "#fef3c7",
    borderRadius: "3px",
    padding: "0 3px",
    boxShadow: "none",
  },
});

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
          <mark key={i} className={isMe ? mentionMeStyles : mentionStyles}>
            {part}
          </mark>
        );
      })}
    </>
  );
}
