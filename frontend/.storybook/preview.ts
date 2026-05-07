import type { Preview } from "@storybook/nextjs-vite";
import { themes } from "@storybook/theming";
import "../src/app/globals.css";

const preview: Preview = {
  parameters: {
    docs: {
      theme: themes.dark,
    },
    backgrounds: {
      default: "dark",
      values: [{ name: "dark", value: "#000000" }],
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    a11y: {
      test: "todo",
    },
  },
};

export default preview;
