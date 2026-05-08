import type { Preview } from "@storybook/nextjs-vite";

import "../src/app/globals.css";
import { WebSocketMock } from "../src/tests/mocks/WebSocketMock";
import { worker } from "../src/tests/msw/browser";

if (typeof window !== "undefined") {
  Object.defineProperty(window, "WebSocket", {
    value: WebSocketMock,
    writable: true,
    configurable: true,
  });
}

const mswReady =
  typeof window !== "undefined"
    ? worker.start({
        serviceWorker: { url: "/mockServiceWorker.js" },
        onUnhandledRequest: "bypass",
      })
    : Promise.resolve();

const preview: Preview = {
  loaders: [
    async () => {
      await mswReady;
    },
  ],
  parameters: {
    docs: {
      backgrounds: "000000",
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
