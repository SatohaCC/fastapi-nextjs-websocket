import type { ReactNode } from "react";
import {
  bubbleMeStyles,
  bubbleOtherStyles,
  bubbleStyles,
  messagePendingStyles,
  messageWrapperMeStyles,
  messageWrapperOtherStyles,
  messageWrapperStyles,
  senderNameStyles,
  timestampMeStyles,
  timestampOtherStyles,
  timestampStyles,
} from "./MessageBubble.styles";

interface MessageBubbleProps {
  username: string;
  currentUser: string;
  textElement: ReactNode;
  timeStr: string;
  isPending?: boolean;
}

export function MessageBubble({
  username,
  currentUser,
  textElement,
  timeStr,
  isPending = false,
}: MessageBubbleProps) {
  const isMe = username === currentUser;

  return (
    <article
      className={`${messageWrapperStyles} ${
        isMe ? messageWrapperMeStyles : messageWrapperOtherStyles
      } ${isPending ? messagePendingStyles : ""}`}
      aria-label={
        isMe ? "あなたからのメッセージ" : `${username} からのメッセージ`
      }
    >
      {!isMe && <span className={senderNameStyles}>{username}</span>}
      <div
        className={`${bubbleStyles} ${
          isMe ? bubbleMeStyles : bubbleOtherStyles
        }`}
      >
        {textElement}
      </div>
      <time
        className={`${timestampStyles} ${
          isMe ? timestampMeStyles : timestampOtherStyles
        }`}
      >
        {timeStr}
      </time>
    </article>
  );
}
