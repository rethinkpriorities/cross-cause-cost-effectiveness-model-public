import { optimizeLodashImports } from "@optimize-lodash/rollup-plugin";
import { sentryVitePlugin } from "@sentry/vite-plugin";
import react from "@vitejs/plugin-react-swc";
import UnoCSS from "unocss/vite";
import { defineConfig, splitVendorChunkPlugin } from "vite";
import checker from "vite-plugin-checker";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    UnoCSS(),
    react({
      plugins: [
        ["@swc-jotai/debug-label", {}],
        ["@swc-jotai/react-refresh", {}],
      ],
    }),
    optimizeLodashImports(),
    checker({
      typescript: true,
      terminal: false,
      overlay: {
        // Make the error overlay less intrusive
        initialIsOpen: false,
      },
    }),
    sentryVitePlugin({
      org: "rethink-priorities",
      project: "ccm-react",
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
    splitVendorChunkPlugin(),
  ],

  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // State management + utilities
          if (
            id.includes("lodash-es") ||
            id.includes("@tanstack") ||
            id.includes("@radix-ui") ||
            id.includes("jotai")
          ) {
            return "state";
          }
          // Chunk plotting related stuff
          if (id.includes("d3") || id.includes("observablehq/plot")) {
            return "plotting";
          }
          // Sentry
          if (id.includes("sentry")) {
            return "sentry";
          }
        },
      },
    },
  },
});
