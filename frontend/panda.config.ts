import { defineConfig } from "@pandacss/dev";

export default defineConfig({
  preflight: true,
  include: ["./src/**/*.{js,jsx,ts,tsx}", "./app/**/*.{js,jsx,ts,tsx}"],
  exclude: [],
  outdir: "src/styled-system",

  theme: {
    extend: {
      tokens: {
        colors: {
          // Brand
          primary: { value: "#1a73e8" },
          primaryHover: { value: "#1557b0" },

          // Backgrounds
          bg: { value: "#F8F9FA" },
          workspaceBg: { value: "#F0F2F5" },
          panelBg: { value: "#FFFFFF" },

          // Borders
          panelBorder: { value: "#DADCE0" },
          border: {
            default: { value: "#E0E0E0" },
            divider: { value: "#EEEEEE" },
            muted: { value: "#BDBDBD" },
            overlay: { value: "rgba(0,0,0,0.08)" },
            errorOverlay: { value: "rgba(217,48,37,0.2)" },
          },

          // Text
          textPrimary: { value: "#202124" },
          textSecondary: { value: "#5F6368" },
          textMuted: { value: "#767676" },
          textBody: { value: "#3C4043" },

          // Interactive surfaces
          surface: {
            subtle: { value: "#F1F3F4" },
            active: { value: "#E8F0FE" },
          },

          // Disabled state
          disabled: {
            bg: { value: "#E8EAED" },
          },

          // Semantic
          warning: { value: "#E37400" },
          error: { value: "#D93025" },
          success: { value: "#1E8E3E" },

          // Status (for badge/indicator variants)
          status: {
            requested: { value: "#E37400" },
            processing: { value: "#1a73e8" },
            completed: { value: "#1E8E3E" },
          },

          // Badge backgrounds
          badge: {
            requestedBg: { value: "#FEF3E2" },
            processingBg: { value: "#E8F0FE" },
            completedBg: { value: "#E6F4EA" },
            errorBg: { value: "#FCE8E6" },
            defaultBg: { value: "#F1F3F4" },
          },

          // Mention highlights
          mention: {
            bg: { value: "rgba(26,115,232,0.1)" },
            meBg: { value: "rgba(227,116,0,0.1)" },
            inBubbleBg: { value: "rgba(255,255,255,0.22)" },
            meInBubbleColor: { value: "#FFF3E0" },
          },

          // Toast (intentionally distinct from main palette)
          toast: {
            text: { value: "#0f1419" },
            subtext: { value: "#536471" },
          },
        },

        radii: {
          tag: { value: "4px" }, // inline tags, mention highlights
          control: { value: "8px" }, // ALL buttons, inputs, selects
          panel: { value: "12px" }, // ALL cards, panels, dropdowns, toasts
          bubble: { value: "18px" }, // chat message bubbles
          pill: { value: "24px" }, // pill-shaped controls
          full: { value: "9999px" }, // badges, toggle track, status pills
        },

        shadows: {
          card: {
            value: "0 1px 4px rgba(0,0,0,0.10), 0 4px 16px rgba(0,0,0,0.06)",
          },
          cardHover: {
            value: "0 2px 8px rgba(0,0,0,0.14), 0 6px 20px rgba(0,0,0,0.08)",
          },
          header: { value: "0 1px 6px rgba(0,0,0,0.10)" },
          panel: {
            value: "0 4px 16px rgba(0,0,0,0.12), 0 1px 4px rgba(0,0,0,0.08)",
          },
          dropdown: {
            value: "0 4px 24px rgba(0,0,0,0.14), 0 1px 6px rgba(0,0,0,0.08)",
          },
          modal: {
            value: "0 2px 8px rgba(0,0,0,0.12), 0 8px 32px rgba(0,0,0,0.08)",
          },
          subtle: { value: "0 1px 3px rgba(0,0,0,0.06)" },
          thumb: { value: "0 1px 3px rgba(0,0,0,0.3)" },
          bubble: { value: "0 1px 3px rgba(26,115,232,0.25)" },
          toast: { value: "0 4px 16px rgba(0,0,0,0.12)" },
          focus: { value: "0 0 0 3px rgba(26,115,232,0.3)" },
          focusSubtle: { value: "0 0 0 3px rgba(26,115,232,0.15)" },
          focusOuter: { value: "0 0 0 5px rgba(26,115,232,0.2)" },
          buttonDefault: {
            value:
              "0 1px 2px rgba(60,64,67,0.3), 0 1px 3px rgba(60,64,67,0.15)",
          },
          buttonHover: {
            value:
              "0 1px 3px rgba(60,64,67,0.3), 0 2px 6px rgba(60,64,67,0.15)",
          },
        },

        fonts: {
          main: {
            value:
              '"Roboto", "Google Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
          },
        },
      },
    },
  },
});
