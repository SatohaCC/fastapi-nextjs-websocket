"use client";

import { Button } from "@/components/ui/Button/Button";
import { Card, CardHeader } from "@/components/ui/Card/Card";
import { Input } from "@/components/ui/Input/Input";
import type { GlobalChatMessage } from "@/types/ws";
import styles from "./GlobalChat.module.css";

interface Props {
  messages: GlobalChatMessage[];
  currentUser: string;
  text: string;
  onTextChange: (value: string) => void;
  onSend: (e: React.FormEvent) => void;
  formatTime: (dateStr: string) => string;
}

export function GlobalChat({
  messages,
  currentUser,
  text,
  onTextChange,
  onSend,
  formatTime,
}: Props) {
  return (
    <Card className={`fade-in ${styles.container}`}>
      <CardHeader className={styles.header}>
        <div>
          <h2 className={styles.title}>Global Chat</h2>
          <p className={styles.subtitle}>全員のChatを表示。</p>
        </div>
      </CardHeader>

      <div className={styles.messagesArea}>
        {messages
          .slice()
          .reverse()
          .map((m) => {
            const isMe = m.username === currentUser;
            return (
              <div
                key={m.id}
                className={`${styles.messageWrapper} ${
                  isMe ? styles.messageWrapperMe : styles.messageWrapperOther
                }`}
              >
                {!isMe && (
                  <span className={styles.senderName}>{m.username}</span>
                )}
                <div
                  className={`${styles.bubble} ${
                    isMe ? styles.bubbleMe : styles.bubbleOther
                  }`}
                >
                  {m.text}
                </div>
                <span
                  className={`${styles.timestamp} ${
                    isMe ? styles.timestampMe : styles.timestampOther
                  }`}
                >
                  {formatTime(m.created_at)}
                </span>
              </div>
            );
          })}
      </div>

      <form onSubmit={onSend} className={styles.inputForm}>
        <Input
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
    </Card>
  );
}
