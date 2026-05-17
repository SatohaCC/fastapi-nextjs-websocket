import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "@storybook/test";
import { useRef, useState } from "react";
import type { GlobalChatServerMessage } from "@/types/ws";
import { useChatSync } from "./useChatSync";

const TestHookComponent = () => {
  const [chatMessages, setChatMessages] = useState<GlobalChatServerMessage[]>(
    [],
  );
  const lastChatId = useRef<number | null>(null);
  const [syncStatus, setSyncStatus] = useState<string>("未同期");

  const { fetchChatMissing } = useChatSync(
    "mock-token",
    setChatMessages,
    lastChatId,
    setSyncStatus,
  );

  return (
    <div style={{ padding: "20px", border: "1px solid #ccc" }}>
      <h3>useChatSync Test</h3>
      <p data-testid="sync-status">Status: {syncStatus}</p>
      <p data-testid="chat-count">Messages: {chatMessages.length}</p>
      <button
        type="button"
        data-testid="sync-button"
        onClick={() => fetchChatMissing()}
      >
        Manual Sync
      </button>
      <div data-testid="message-list">
        {chatMessages.map((m) => (
          <div key={m.id}>{m.text}</div>
        ))}
      </div>
    </div>
  );
};

const meta: Meta<typeof TestHookComponent> = {
  title: "Hooks/useChatSync",
  component: TestHookComponent,
};

export default meta;
type Story = StoryObj<typeof TestHookComponent>;

export const SyncSuccess: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await expect(canvas.getByTestId("sync-status")).toHaveTextContent("未同期");
    await expect(canvas.getByTestId("chat-count")).toHaveTextContent("0");

    await userEvent.click(canvas.getByTestId("sync-button"));

    const message = await canvas.findByText("auto-sync message");
    await expect(message).toBeInTheDocument();
    await expect(canvas.getByTestId("chat-count")).toHaveTextContent("1");
    await expect(canvas.getByTestId("sync-status")).toHaveTextContent(
      /最終同期:/,
    );
  },
};
