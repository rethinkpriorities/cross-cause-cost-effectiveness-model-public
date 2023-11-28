import { presetForms } from "@julr/unocss-preset-forms";
import presetIcons from "@unocss/preset-icons";
import presetUno from "@unocss/preset-uno";
import transformerDirectives from "@unocss/transformer-directives";
import { defineConfig, presetTypography, presetWebFonts } from "unocss";
import { presetDaisy } from "unocss-preset-daisy";
import { presetRadixUi } from "unocss-preset-primitives";

export default defineConfig({
  presets: [
    presetUno({
      dark: "media",
    }),
    presetIcons(),
    presetWebFonts({
      provider: "google",
      fonts: {
        sans: "IBM Plex Sans",
        mono: "IBM Plex Mono",
        serif: "IBM Plex Serif",
      },
    }),
    presetTypography(),
    presetForms(),
    presetDaisy({
      themes: ["corporate"],
    }),
    presetRadixUi(),
  ],
  theme: {
    colors: {
      dashboard: {
        // Background colors
        light: "#f9f9f9",
        dark: "#171717",
        gray: "#424242",
        // Text colors
      },
    },
  },
  transformers: [transformerDirectives()],
  content: {
    pipeline: {
      include: [/\.([jt]sx|mdx?|html)($|\?)/, "**/@quri*.js"],
    },
  },
  blocklist: [
    // This hides a warning when compiling the squiggle utilities
    // but if it's needed it can be re-enabled
    "container",
  ],
  safelist: [
    "grow",
    // Background colors
    "bg-dashboard-light",
    "dark:bg-dashboard-dark",
  ],
});
