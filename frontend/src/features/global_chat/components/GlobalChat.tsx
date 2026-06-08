"use client";

import { PanelLayout } from "@/components/ui/composites/PanelLayout/PanelLayout";
import { Button } from "@/components/ui/primitives/Button/Button";
import { Input } from "@/components/ui/primitives/Input/Input";
import { css } from "@/styled-system/css";
import type { GlobalChatServerMessage } from "@/types/ws";
import { MentionText } from "./Mention/MentionText";
import { MentionDropdown } from "./MentionDropdown/MentionDropdown";
import { MessageBubble } from "./MessageBubble/MessageBubble";
import { TypingIndicator } from "./TypingIndicator/TypingIndicator";

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

const inputFormStyles = css({
  padding: "12px 16px",
  display: "flex",
  gap: "8px",
  alignItems: "center",
});

const inputWrapperStyles = css({
  position: "relative",
  flex: 1,
  minWidth: 0,
});

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
    <PanelLayout
      header={
        <>
          <h2
            className={css({
              fontSize: "15px",
              fontWeight: 500,
              color: "textPrimary",
              letterSpacing: "0.01em",
            })}
          >
            Global Chat
          </h2>
          <p
            className={css({
              fontSize: "12px",
              color: "textSecondary",
              marginTop: "2px",
            })}
          >
            参加者全員とリアルタイムで会話できます。
          </p>
        </>
      }
      form={
        <>
          <TypingIndicator typingUsers={typingUsers} />
          <form onSubmit={onSend} className={inputFormStyles}>
            <div className={inputWrapperStyles}>
              {mentionIsOpen && (
                <MentionDropdown
                  suggestions={mentionSuggestions}
                  focusedIndex={mentionFocusedIndex}
                  onSelect={onMentionSelect}
                />
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
        </>
      }
      padding="normal"
      contentRole="log"
      contentAriaLabel="グローバルチャットのメッセージ履歴"
    >
      {messages.map((m) => {
        return (
          <MessageBubble
            key={m.id}
            username={m.username}
            currentUser={currentUser}
            textElement={
              <MentionText
                text={m.text}
                currentUser={currentUser}
                isInMeBubble={m.username === currentUser}
              />
            }
            timeStr={formatTime(m.created_at)}
            isPending={m.isPending}
          />
        );
      })}
      <div ref={bottomRef} />
    </PanelLayout>
  );
}
