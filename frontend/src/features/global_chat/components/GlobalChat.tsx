"use client";

import { Button } from "@/components/ui/Button/Button";
import { Card, CardHeader } from "@/components/ui/Card/Card";
import { Input } from "@/components/ui/Input/Input";
import { css } from "@/styled-system/css";
import type { GlobalChatServerMessage } from "@/types/ws";
import { MentionText } from "./MentionText";
import { TypingIndicator } from "./TypingIndicator";

const panelStyles = css({
  gridRow: "span 3",
  display: "grid",
  gridTemplateRows: "subgrid",
  "@media (max-width: 1024px)": {
    gridRow: "unset",
    display: "flex",
    flexDirection: "column",
  },
});

const titleStyles = css({
  fontSize: "17px",
  fontWeight: 800,
});

const subtitleStyles = css({
  fontSize: "12px",
  color: "textSecondary",
});

const messagesAreaStyles = css({
  padding: "20px",
  display: "flex",
  flexDirection: "column",
  gap: "12px",
  overflowY: "auto",
  minHeight: 0,
});

const formWrapperStyles = css({
  borderTop: "1px solid",
  borderColor: "panelBorder",
  display: "flex",
  flexDirection: "column",
  justifyContent: "flex-end",
});

const messageWrapperStyles = css({
  maxWidth: "85%",
  display: "flex",
  flexDirection: "column",
});

const messageWrapperMeStyles = css({
  alignSelf: "flex-end",
  alignItems: "flex-end",
});

const messageWrapperOtherStyles = css({
  alignSelf: "flex-start",
  alignItems: "flex-start",
});

const senderNameStyles = css({
  fontSize: "11px",
  fontWeight: 700,
  marginBottom: "4px",
  marginLeft: "4px",
  color: "textSecondary",
});

const bubbleStyles = css({
  padding: "10px 16px",
  fontSize: "14px",
  lineHeight: 1.5,
  color: "white",
});

const bubbleMeStyles = css({
  borderRadius: "22px 22px 4px 22px",
  background: "primary",
});

const bubbleOtherStyles = css({
  borderRadius: "22px 22px 22px 4px",
  background: "#262626",
});

const timestampStyles = css({
  fontSize: "11px",
  color: "textSecondary",
  marginTop: "4px",
});

const timestampMeStyles = css({
  marginRight: "4px",
});

const timestampOtherStyles = css({
  marginLeft: "4px",
});

const inputFormStyles = css({
  padding: "16px 20px",
  display: "flex",
  gap: "12px",
  alignItems: "center",
});

const textInputStyles = css({
  borderRadius: "20px",
  background: "#16181c",
  border: "1px solid transparent",
  flex: 1,
});

const sendButtonStyles = css({
  padding: "10px 24px",
});

const messagePendingStyles = css({
  opacity: 0.5,
});

const inputWrapperStyles = css({
  position: "relative",
  flex: 1,
});

const mentionDropdownStyles = css({
  position: "absolute",
  bottom: "calc(100% + 6px)",
  left: 0,
  right: 0,
  background: "#1e2024",
  border: "1px solid",
  borderColor: "panelBorder",
  borderRadius: "12px",
  listStyle: "none",
  margin: 0,
  padding: "4px",
  zIndex: 10,
  boxShadow: "0 4px 16px rgba(0, 0, 0, 0.4)",
});

const mentionItemStyles = css({
  display: "block",
  width: "100%",
  padding: "8px 12px",
  fontSize: "13px",
  borderRadius: "8px",
  cursor: "pointer",
  color: "textPrimary",
  background: "transparent",
  border: "none",
  textAlign: "left",
  _hover: {
    background: "#2a2d33",
  },
  _focusVisible: {
    background: "#2a2d33",
    outline: "none",
    boxShadow: "inset 0 0 0 2px {colors.primary}",
  },
});

const mentionItemFocusedStyles = css({
  background: "#2a2d33",
});

export interface GlobalChatProps {
  messages: (GlobalChatServerMessage & { isPending?: boolean })[];
  currentUser: string;
  text: string;
  onTextChange: (value: string) => void;
  onSend: (e: React.FormEvent) => void;
  onInputKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  formatTime: (dateStr: string) => string;
  bottomRef: React.RefObject<HTMLDivElement | null>;
  typingUsers: Set<string>;
  mentionIsOpen: boolean;
  mentionSuggestions: string[];
  mentionFocusedIndex: number;
  onMentionSelect: (username: string) => void;
}

export function GlobalChat({
  messages,
  currentUser,
  text,
  onTextChange,
  onSend,
  onInputKeyDown,
  formatTime,
  bottomRef,
  typingUsers,
  mentionIsOpen,
  mentionSuggestions,
  mentionFocusedIndex,
  onMentionSelect,
}: GlobalChatProps) {
  return (
    <Card className={`fade-in ${panelStyles}`}>
      <CardHeader>
        <h2 className={titleStyles}>Global Chat</h2>
        <p className={subtitleStyles}>
          参加者全員とリアルタイムで会話できます。
        </p>
      </CardHeader>
      <div
        className={messagesAreaStyles}
        role="log"
        aria-label="グローバルチャットのメッセージ履歴"
        aria-live="polite"
      >
        {messages.map((m) => {
          const isMe = m.username === currentUser;
          return (
            <article
              key={m.id}
              className={`${messageWrapperStyles} ${
                isMe ? messageWrapperMeStyles : messageWrapperOtherStyles
              } ${m.isPending ? messagePendingStyles : ""}`}
              aria-label={
                isMe
                  ? "あなたからのメッセージ"
                  : `${m.username} からのメッセージ`
              }
            >
              {!isMe && <span className={senderNameStyles}>{m.username}</span>}
              <div
                className={`${bubbleStyles} ${
                  isMe ? bubbleMeStyles : bubbleOtherStyles
                }`}
              >
                <MentionText text={m.text} currentUser={currentUser} />
              </div>
              <time
                dateTime={m.created_at}
                className={`${timestampStyles} ${
                  isMe ? timestampMeStyles : timestampOtherStyles
                }`}
              >
                {formatTime(m.created_at)}
              </time>
            </article>
          );
        })}
        <div ref={bottomRef} />
      </div>
      <div className={formWrapperStyles}>
        <TypingIndicator typingUsers={typingUsers} />
        <form onSubmit={onSend} className={inputFormStyles}>
          <div className={inputWrapperStyles}>
            {mentionIsOpen && (
              <div className={mentionDropdownStyles}>
                {mentionSuggestions.map((u, i) => (
                  <button
                    key={u}
                    type="button"
                    className={`${mentionItemStyles} ${
                      i === mentionFocusedIndex ? mentionItemFocusedStyles : ""
                    }`}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      onMentionSelect(u);
                    }}
                  >
                    @{u}
                  </button>
                ))}
              </div>
            )}
            <label htmlFor="global-chat-input" className="sr-only">
              メッセージを入力
            </label>
            <Input
              id="global-chat-input"
              type="text"
              value={text}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                onTextChange(e.target.value)
              }
              onKeyDown={onInputKeyDown}
              placeholder="Start a new message"
              className={textInputStyles}
              autoComplete="off"
            />
          </div>
          <Button
            type="submit"
            variant="primary"
            className={sendButtonStyles}
            disabled={!text.trim()}
          >
            Send
          </Button>
        </form>
      </div>
    </Card>
  );
}
