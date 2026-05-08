import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "@storybook/test";
import { useMessageSync } from "./useMessageSync";

// Hook を使用するテスト用コンポーネント
const TestHookComponent = () => {
  const { chatMessages, syncStatus, fetchMissingFeeds } =
    useMessageSync("mock-token");

  return (
    <div style={{ padding: "20px", border: "1px solid #ccc" }}>
      <h3>useMessageSync Test</h3>
      <p data-testid="sync-status">Status: {syncStatus}</p>
      <p data-testid="chat-count">Messages: {chatMessages.length}</p>
      <button
        type="button"
        data-testid="sync-button"
        onClick={() => fetchMissingFeeds()}
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
  title: "Hooks/useMessageSync",
  component: TestHookComponent,
};

export default meta;
type Story = StoryObj<typeof TestHookComponent>;

export const SyncSuccess: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // 初期状態の検証
    await expect(canvas.getByTestId("sync-status")).toHaveTextContent("未同期");
    await expect(canvas.getByTestId("chat-count")).toHaveTextContent("0");

    // 同期ボタンをクリック
    await userEvent.click(canvas.getByTestId("sync-button"));

    // MSW のレスポンスを待機して検証
    // expect.poll は @storybook/test には無いため、findBy を使用
    const message = await canvas.findByText("auto-sync message");
    await expect(message).toBeInTheDocument();
    await expect(canvas.getByTestId("chat-count")).toHaveTextContent("1");
    await expect(canvas.getByTestId("sync-status")).toHaveTextContent(
      /最終同期:/,
    );
  },
};
