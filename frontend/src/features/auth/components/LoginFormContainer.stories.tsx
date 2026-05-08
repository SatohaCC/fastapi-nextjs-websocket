import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, waitFor, within } from "@storybook/test";
import { LoginFormContainer } from "./LoginFormContainer";

const meta: Meta<typeof LoginFormContainer> = {
  title: "Features/Auth/LoginFormContainer",
  component: LoginFormContainer,
  parameters: {
    nextjs: {
      appDirectory: true,
    },
  },
};

export default meta;
type Story = StoryObj<typeof LoginFormContainer>;

export const LoginFlow: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    const usernameInput = canvas.getByLabelText(/ユーザー名/i);
    const passwordInput = canvas.getByLabelText(/パスワード/i);
    const submitButton = canvas.getByRole("button", { name: /ログイン/i });

    // 入力
    await userEvent.clear(usernameInput);
    await userEvent.type(usernameInput, "testuser");
    await userEvent.clear(passwordInput);
    await userEvent.type(passwordInput, "testpass");

    // ログイン実行
    await userEvent.click(submitButton);

    // MSW のレスポンスと sessionStorage の更新を待機
    await waitFor(() => {
      expect(sessionStorage.getItem("token")).toBe("mock-token");
    });
    expect(sessionStorage.getItem("username")).toBe("testuser");
  },
};
