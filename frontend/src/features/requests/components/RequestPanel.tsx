"use client";

import { Badge } from "@/components/ui/Badge/Badge";
import { Button } from "@/components/ui/Button/Button";
import { Card, CardHeader } from "@/components/ui/Card/Card";
import { Input, Select } from "@/components/ui/Input/Input";
import type { RequestMessage, RequestStatus } from "@/types/ws";
import styles from "./RequestPanel.module.css";

interface Props {
  otherUsers: string[];
  requests: RequestMessage[];
  currentUser: string;
  targetUser: string;
  text: string;
  onTargetUserChange: (value: string) => void;
  onTextChange: (value: string) => void;
  onSend: (e: React.FormEvent) => void;
  onUpdateStatus: (id: number, status: RequestStatus) => void;
  formatDate: (dateStr: string) => string;
}

export function RequestPanel({
  otherUsers,
  requests,
  currentUser,
  targetUser,
  text,
  onTargetUserChange,
  onTextChange,
  onSend,
  onUpdateStatus,
  formatDate,
}: Props) {
  return (
    <Card className={`fade-in ${styles.container}`}>
      <CardHeader>
        <h2 className={styles.title}>ダイレクトリクエスト</h2>
        <p className={styles.subtitle}>タスクの依頼や問い合わせ</p>
      </CardHeader>

      <form onSubmit={onSend} className={styles.requestForm}>
        <div className={styles.formGrid}>
          <div className={styles.inputGroup}>
            <Select
              value={targetUser}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                onTargetUserChange(e.target.value)
              }
              className={styles.selectRecipient}
              aria-label="Select recipient"
            >
              <option value="" disabled>
                依頼先を選択
              </option>
              {otherUsers.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </Select>
            <Input
              type="text"
              value={text}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                onTextChange(e.target.value)
              }
              placeholder="依頼内容を入力してください"
              className={styles.inputTask}
              aria-label="依頼内容"
            />
          </div>
          <Button
            type="submit"
            variant="primary"
            className={styles.submitButton}
            disabled={!targetUser || !text.trim()}
          >
            リクエストを送信
          </Button>
        </div>
      </form>

      <div className={styles.requestList}>
        {requests.length === 0 ? (
          <div className={styles.emptyState}>現在リクエストはありません。</div>
        ) : (
          requests.map((m) => {
            const isFromMe = m.sender === currentUser;
            const canUpdate =
              m.recipient === currentUser && m.status !== "completed";

            return (
              <div key={m.id} className={`tweet-card ${styles.requestItem}`}>
                <div className={styles.itemHeader}>
                  <div className={styles.metaInfo}>
                    <div className={styles.senderName}>
                      {isFromMe ? `${m.recipient} への依頼` : m.sender}
                    </div>
                    {!isFromMe && (
                      <div className={styles.senderHandle}>
                        @{m.sender.toLowerCase()}
                      </div>
                    )}
                    <div className={styles.separator}>·</div>
                    <div className={styles.timestamp}>
                      {formatDate(m.created_at)}
                    </div>
                  </div>
                  <Badge variant={m.status}>
                    {m.status === "requested" && "未着手"}
                    {m.status === "processing" && "進行中"}
                    {m.status === "completed" && "完了"}
                  </Badge>
                </div>

                <div className={styles.requestText}>{m.text}</div>

                {canUpdate && (
                  <div className={styles.actionGroup}>
                    {m.status === "requested" && (
                      <Button
                        type="button"
                        onClick={() => onUpdateStatus(m.id, "processing")}
                        variant="secondary"
                        className={styles.actionButton}
                      >
                        承諾
                      </Button>
                    )}
                    <Button
                      type="button"
                      onClick={() => onUpdateStatus(m.id, "completed")}
                      variant="primary"
                      className={`${styles.actionButton} ${styles.completeButton}`}
                    >
                      完了
                    </Button>
                  </div>
                )}

                {m.status === "completed" && (
                  <div className={styles.resolvedNote}>
                    ✓ 解決済み: {formatDate(m.updated_at)}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}
