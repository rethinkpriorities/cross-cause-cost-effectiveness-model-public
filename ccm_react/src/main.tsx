import "@radix-ui/themes/styles.css";
import { RouterProvider } from "@tanstack/react-router";
import { Provider as JotaiProvider, createStore } from "jotai";
import { DevTools } from "jotai-devtools";
import React from "react";
import ReactDOM from "react-dom/client";
import "virtual:uno.css";
import "./main.css";

import { Theme } from "@radix-ui/themes";

import { OpenAPI } from "./client/index.ts";
import router from "./routes/router.tsx";

import * as Sentry from "@sentry/react";

import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./utils/query-client.ts";

import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

if (import.meta.env.PROD) {
  Sentry.init({
    dsn: "https://c99805daf5cc1f4e3858fe39021365ee@o4505964725796864.ingest.sentry.io/4505964732678144",
    integrations: [
      new Sentry.BrowserTracing(),
      new Sentry.BrowserProfilingIntegration(),
      new Sentry.Replay({
        // We don't have any PII in the UI
        // see https://docs.sentry.io/platforms/javascript/session-replay/privacy/
        maskAllText: false,
        maskAllInputs: false,
      }),
    ],
    // Controls for which URLs distributed tracing should be enabled
    // https://docs.sentry.io/platforms/javascript/performance/instrumentation/automatic-instrumentation/
    tracePropagationTargets: [
      "localhost",
      /^https:\/\/ccm\.rethinkpriorities\.org\/api/,
      /^https:\/\/cross-cause-model-579669a29b63\.herokuapp\.com\//,
      /^https:\/\/cross-cause-model-staging-5d2f14771f61\.herokuapp\.com\//,
    ],
    // Tracing
    tracesSampleRate: 0.5,
    // Profiling (a fraction of tracesSampleRate)
    profilesSampleRate: 0.2,
    // Session Replay
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  });
}

OpenAPI.BASE = (import.meta.env.VITE_BASE_URL ||
  "http://localhost:8000") as string;

const jotaiStore = createStore();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <JotaiProvider store={jotaiStore}>
      <DevTools store={jotaiStore} />
      <QueryClientProvider client={queryClient}>
        <Theme appearance="light" accentColor="blue" panelBackground="solid">
          <RouterProvider router={router} />
        </Theme>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </JotaiProvider>
  </React.StrictMode>,
);
