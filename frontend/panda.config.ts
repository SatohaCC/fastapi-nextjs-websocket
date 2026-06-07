import { defineConfig } from "@pandacss/dev";

export default defineConfig({
  // Whether to use css reset
  preflight: true,

  // Where to look for your css declarations
  include: ["./src/**/*.{js,jsx,ts,tsx}"],

  // Files to exclude
  exclude: [],

  // The output directory for your css system
  outdir: "src/styled-system",

  // Useful for theme customization
  theme: {
    extend: {
      tokens: {
        colors: {
          primary: { value: "#1d9bf0" },
          primaryHover: { value: "#1a8cd8" },
          bg: { value: "#000000" },
          panelBg: { value: "#000000" },
          panelBorder: { value: "#2f3336" },
          textPrimary: { value: "#e7e9ea" },
          textSecondary: { value: "#8e959c" },
          warning: { value: "#ffd400" },
          error: { value: "#ff6b7a" },
          status: {
            requested: { value: "#ffd400" },
            processing: { value: "#1d9bf0" },
            completed: { value: "#00ba7c" },
          },
        },
        fonts: {
          main: {
            value:
              '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
          },
        },
      },
    },
  },
});
