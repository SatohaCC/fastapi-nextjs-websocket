"use client";

import {Button} from "@/components/ui/Button/Button";
import {Card, CardHeader} from "@/components/ui/Card/Card";
import {Input} from "@/components/ui/Input/Input";
import type {GlobalChatServerMessage} from "@/types/ws";
import styles from "./GlobalChat.module.css";

export interface GlobalChatProps {
  messages: (GlobalChatServerMessage & { isPending?: boolean })[];
  currentUser: string;
  text: string;
  onTextChange: (value: string) => void;
  onSend: (e: React.FormEvent) => void;
  formatTime: (dateStr: string) => string;
  bottomRef: React.RefObject<HTMLDivElement | null>;
}

export function GlobalChat({
  messages,
  currentUser,
  text,
  onTextChange,
  onSend,
  formatTime,
  bottomRef,
}: GlobalChatProps) {
  return (
    <Card className={`fade-in ${styles.panel}`}>
      <CardHeader>
        <h2 className={styles.title}>Global Chat</h2>
        <p className={styles.subtitle}>
          参加者全員とリアルタイムで会話できます。
        </p>
      </CardHeader>
      <div
        className={styles.messagesArea}
        role="log"
        aria-label="グローバルチャットのメッセージ履歴"
        aria-live="polite"
      >
        {messages.map((m) => {
          const isMe = m.username === currentUser;
          return (
            <article
              key={m.id}
              className={`${styles.messageWrapper} ${
                isMe ? styles.messageWrapperMe : styles.messageWrapperOther
              } ${m.isPending ? styles.messagePending : ""}`}
              aria-label={
                isMe
                  ? "あなたからのメッセージ"
                  : `${m.username} からのメッセージ`
              }
            >
              {!isMe && <span className={styles.senderName}>{m.username}</span>}
              <div
                className={`${styles.bubble} ${
                  isMe ? styles.bubbleMe : styles.bubbleOther
                }`}
              >
                {m.text}
              </div>
              <time
                dateTime={m.created_at}
                className={`${styles.timestamp} ${
                  isMe ? styles.timestampMe : styles.timestampOther
                }`}
              >
                {formatTime(m.created_at)}
              </time>
            </article>
          );
        })}
        <div ref={bottomRef} />
      </div>
      <div className={styles.formWrapper}>
        <form onSubmit={onSend} className={styles.inputForm}>
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
            placeholder="Start a new message"
            className={styles.textInput}
            autoComplete="off"
          />
          <Button
            type="submit"
            variant="primary"
            className={styles.sendButton}
            disabled={!text.trim()}
          >
            Send
          </Button>
        </form>
      </div>
    </Card>
  );
}
