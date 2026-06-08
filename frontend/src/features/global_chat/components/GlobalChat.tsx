"use client";

import { Button } from "@/components/ui/Button/Button";
import { Card, CardHeader } from "@/components/ui/Card/Card";
import { Input } from "@/components/ui/Input/Input";
import type { GlobalChatServerMessage } from "@/types/ws";
import {
  bubbleMeStyles,
  bubbleOtherStyles,
  bubbleStyles,
  formWrapperStyles,
  inputFormStyles,
  inputWrapperStyles,
  mentionAvatarStyles,
  mentionDropdownStyles,
  mentionHandleStyles,
  mentionItemFocusedStyles,
  mentionItemStyles,
  mentionUserInfoStyles,
  mentionUsernameStyles,
  messagePendingStyles,
  messagesAreaStyles,
  messageWrapperMeStyles,
  messageWrapperOtherStyles,
  messageWrapperStyles,
  panelStyles,
  senderNameStyles,
  subtitleStyles,
  timestampMeStyles,
  timestampOtherStyles,
  timestampStyles,
  titleStyles,
} from "./GlobalChat.styles";
import { MentionText } from "./MentionText";
import { TypingIndicator } from "./TypingIndicator";

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
    <div className={`fade-in ${panelStyles}`}>
      <Card>
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
                {!isMe && (
                  <span className={senderNameStyles}>{m.username}</span>
                )}
                <div
                  className={`${bubbleStyles} ${
                    isMe ? bubbleMeStyles : bubbleOtherStyles
                  }`}
                >
                  <MentionText
                    text={m.text}
                    currentUser={currentUser}
                    isInMeBubble={isMe}
                  />
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
                        i === mentionFocusedIndex
                          ? mentionItemFocusedStyles
                          : ""
                      }`}
                      onMouseDown={(e) => {
                        e.preventDefault();
                        onMentionSelect(u);
                      }}
                    >
                      <span className={mentionAvatarStyles} aria-hidden="true">
                        {u[0]}
                      </span>
                      <span className={mentionUserInfoStyles}>
                        <span className={mentionUsernameStyles}>{u}</span>
                        <span className={mentionHandleStyles}>@{u}</span>
                      </span>
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
                autoComplete="off"
              />
            </div>
            <Button type="submit" variant="primary" disabled={!text.trim()}>
              Send
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
