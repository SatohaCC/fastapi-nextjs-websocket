import { defineConfig } from "@pandacss/dev";

export default defineConfig({
  preflight: true,
  include: ["./src/**/*.{js,jsx,ts,tsx}", "./app/**/*.{js,jsx,ts,tsx}"],
  exclude: [],
  outdir: "src/styled-system",

  conditions: {
    extend: {
      // Single breakpoint for stacked (1-column) layout
      mobile: "@media (max-width: 1024px)",
    },
  },

  theme: {
    extend: {
      keyframes: {
        fadeIn: {
          from: { opacity: 0, transform: "translateY(10px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
        fadeOut: {
          from: { opacity: 1 },
          to: { opacity: 0 },
        },
        shimmer: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(200%)" },
        },
        pulse: {
          "0%, 100%": { opacity: 0.7 },
          "50%": { opacity: 1 },
        },
      },

      tokens: {
        colors: {
          // Brand
          // WCAG 2.2 AA: used both as text on light surfaces (links, ghost
          // buttons, mentions) and as a background under white text.
          // #1557B0 = 6.9:1 on white, >=4.5:1 on all light surface tokens.
          primary: { value: "#1557B0" },
          primaryHover: { value: "#174EA6" },

          // Backgrounds
          bg: { value: "#F8F9FA" },
          workspaceBg: { value: "#F0F2F5" },
          panelBg: { value: "#FFFFFF" },

          // Borders
          panelBorder: { value: "#DADCE0" },
          border: {
            default: { value: "#E0E0E0" },
            divider: { value: "#EEEEEE" },
            // 4.6:1 on white — used for the Toggle off-track and input
            // boundaries, which require >=3:1 (WCAG 1.4.11 non-text contrast).
            muted: { value: "#757575" },
            overlay: { value: "rgba(0,0,0,0.08)" },
            errorOverlay: { value: "rgba(217,48,37,0.2)" },
          },

          // Text
          textPrimary: { value: "#202124" },
          textSecondary: { value: "#5F6368" },
          // 4.75:1 on workspaceBg (worst-case surface); #767676 only passed on
          // pure white.
          textMuted: { value: "#6B6B6B" },
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
          // WCAG 2.2 AA: each value keeps >=4.5:1 both on white and on its
          // paired tinted badge background (see badge.* below).
          warning: { value: "#9F5500" }, // 5.1:1 on badge.requestedBg
          error: { value: "#C5221F" }, // 4.9:1 on badge.errorBg
          success: { value: "#137333" }, // 5.2:1 on badge.completedBg

          // Status (for badge/indicator variants)
          status: {
            requested: { value: "#9F5500" },
            processing: { value: "#1557B0" }, // 6.1:1 on badge.processingBg
            completed: { value: "#137333" },
            onlineBorder: { value: "#34A853" }, // 3.1:1 on white (non-text, >=3:1)
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
            bg: { value: "rgba(21,87,176,0.1)" }, // tracks primary
            meBg: { value: "rgba(159,85,0,0.1)" }, // tracks warning
            // Dark overlay (not white) so white/cream text inside the chip on
            // the primary bubble stays >=4.5:1 (white alpha capped it at 3.2:1).
            inBubbleBg: { value: "rgba(0,0,0,0.22)" },
            meInBubbleColor: { value: "#FFF3E0" },
          },

          // Toast (intentionally distinct from main palette)
          toast: {
            text: { value: "#0f1419" },
            subtext: { value: "#536471" },
          },
        },

        fontSizes: {
          "2xs": { value: "11px" }, // fine print, uppercase labels
          xs: { value: "12px" }, // captions, timestamps, subtitles
          sm: { value: "13px" }, // secondary content, small buttons
          md: { value: "14px" }, // body text, inputs, default buttons
          lg: { value: "15px" }, // panel titles
          xl: { value: "16px" }, // large buttons
          "2xl": { value: "18px" }, // app logo
          "3xl": { value: "26px" }, // login hero logo
          "4xl": { value: "32px" }, // splash logo
          "5xl": { value: "48px" }, // error page heading
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
          bubble: { value: "0 1px 3px rgba(21,87,176,0.25)" },
          toast: { value: "0 4px 16px rgba(0,0,0,0.12)" },
          // Focus ring at 0.65 alpha blends to >=3:1 against white
          // (WCAG 1.4.11); 0.3 alpha was an effective 1.6:1.
          focus: { value: "0 0 0 3px rgba(21,87,176,0.65)" },
          focusSubtle: { value: "0 0 0 3px rgba(21,87,176,0.35)" },
          focusOuter: { value: "0 0 0 5px rgba(21,87,176,0.4)" },
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
