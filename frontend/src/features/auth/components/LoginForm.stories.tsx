import type { Meta, StoryObj } from "@storybook/react";
import { fn } from "@storybook/test";
import { LoginForm } from "./LoginForm";

const meta: Meta<typeof LoginForm> = {
  title: "Features/Auth/LoginForm",
  component: LoginForm,
  tags: ["autodocs"],
  args: {
    onUsernameChange: fn(),
    onPasswordChange: fn(),
    onSubmit: fn(),
  },
};

export default meta;
type Story = StoryObj<typeof LoginForm>;

export const Default: Story = {
  args: {
    username: "",
    password: "",
    error: null,
    loading: false,
  },
};

export const Filled: Story = {
  args: {
    username: "alice",
    password: "password1",
    error: null,
    loading: false,
  },
};

export const Loading: Story = {
  args: {
    username: "alice",
    password: "password1",
    error: null,
    loading: true,
  },
};

export const ErrorState: Story = {
  args: {
    username: "alice",
    password: "wrong-password",
    error: "ユーザー名またはパスワードが正しくありません",
    loading: false,
  },
};
