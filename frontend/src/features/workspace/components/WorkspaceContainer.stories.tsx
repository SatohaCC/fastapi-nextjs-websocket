import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, waitFor, within } from "@storybook/test";
import { WebSocketMock } from "@/tests/mocks/WebSocketMock";
import { WorkspaceContainer } from "./WorkspaceContainer";

const meta: Meta<typeof WorkspaceContainer> = {
  title: "Features/Workspace/WorkspaceContainer",
  component: WorkspaceContainer,
  parameters: {
    nextjs: {
      appDirectory: true,
    },
  },
};

export default meta;
type Story = StoryObj<typeof WorkspaceContainer>;

export const IntegrationTest: Story = {
  beforeEach: () => {
    sessionStorage.setItem("token", "test-token");
    sessionStorage.setItem("username", "alice");
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await waitFor(
      () => {
        expect(canvas.queryByText(/読み込み中/i)).not.toBeInTheDocument();
      },
      { timeout: 5000 },
    );

    // チャットメッセージの入力
    const input = await canvas.findByPlaceholderText(/Start a new message/i);
    await userEvent.type(input, "Hello from test!");

    const sendButton = canvas.getByRole("button", { name: /Send/i });
    await userEvent.click(sendButton);

    // WebSocket からのメッセージ受信をシミュレート
    // useWebSocket 内の connect() が呼ばれて WebSocketMock インスタンスが作成されているはず
    await waitFor(() => {
      expect(WebSocketMock.instances.length).toBeGreaterThan(0);
    });

    const ws = WebSocketMock.lastInstance();

    // オープンを待つ
    await waitFor(() => {
      expect(ws.readyState).toBe(WebSocketMock.OPEN);
    });

    // サーバーからのメッセージをエミュレート
    ws.receive({
      type: "global_chat",
      id: 123,
      username: "bob",
      text: "Nice to meet you!",
      created_at: new Date().toISOString(),
      seq: 1,
    });

    // 画面にメッセージが表示されたか確認
    const receivedMsg = await canvas.findByText("Nice to meet you!");
    expect(receivedMsg).toBeInTheDocument();

    // "bob" はユーザーリストとチャットの両方に出る可能性があるので findAllByText を使用
    const bobElements = await canvas.findAllByText("bob");
    expect(bobElements.length).toBeGreaterThan(0);

    // --- ダイレクトリクエストの受信テスト ---
    ws.receive({
      type: "request",
      id: 456,
      seq: 2,
      sender: "charlie",
      recipient: "alice",
      text: "Can you help me with Phase 4?",
      status: "requested",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });

    // リクエストがリストに表示されたか確認
    const requestMsg = await canvas.findByText("Can you help me with Phase 4?");
    expect(requestMsg).toBeInTheDocument();

    const charlieElements = await canvas.findAllByText("charlie");
    expect(charlieElements.length).toBeGreaterThan(0);
  },
};
