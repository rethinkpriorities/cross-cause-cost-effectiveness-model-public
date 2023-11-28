import { QueryErrorResetBoundary } from "@tanstack/react-query";
import {
  FallbackProps,
  ErrorBoundary as ReactErrorBoundary,
} from "react-error-boundary";
import { P, match } from "ts-pattern";
import { ProjectNotFoundError } from "../../stores/atoms";

interface ParsedError {
  message: string;
  explanation: string;
  stack?: string;
}
type Reset =
  | ((
      details:
        | {
            reason: "imperative-api";
            args: unknown[];
          }
        | {
            reason: "keys";
            prev: unknown[] | undefined;
            next: unknown[] | undefined;
          },
    ) => void)
  | undefined;

export function ErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <QueryErrorResetBoundary>
      {({ reset }: { reset: Reset }) => {
        return (
          <ReactErrorBoundary onReset={reset} FallbackComponent={ErrorFallback}>
            {children}
          </ReactErrorBoundary>
        );
      }}
    </QueryErrorResetBoundary>
  );
}

export function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  const parsedError = match(error)
    .returnType<ParsedError>()
    .with({ message: P.string.includes("NetworkError") }, (_) => ({
      message: "A problem occured when connecting to the server.",
      explanation: "This is probably on us. The server might be down.",
    }))
    .with({ message: P.string.includes("Validation Error") }, (e) => ({
      message: "Your settings are invalid.",
      explanation: `The API has rejected your settings as invalid. This could be a bug or due to a change in the API. You can reset your settings below. The error message was: ${e.message}`,
    }))
    .with(P.instanceOf(ProjectNotFoundError), (e) => ({
      message: "Project not found.",
      explanation: `The project "${e.id}" doesn't exist. Clearing your settings will restore to the default project.`,
    }))
    .with({ message: P.string, stack: P.string }, (e) => ({
      message: "Something went wrong.",
      explanation: `${e.message}`,
      stack: e.stack,
    }))
    .with({ message: P.string }, (e) => ({
      message: "Something went wrong.",
      explanation: `An unexpected error was raised: ${e.message}`,
    }))
    .otherwise(() => ({
      message: "Something went wrong.",
      explanation: "This is unexpected, and you should report this as a bug.",
    }));

  return (
    <div className="min-h-60 flex flex-col justify-between border border-red-400 rounded bg-red-100 px-6 py-8 dark:border-red-700 dark:bg-red-900">
      <div>
        <h2 className="text-lg font-semibold text-red-700 dark:text-red-300">
          {parsedError.message}
        </h2>
        <p className="text-red-600 dark:text-slate-100">
          {parsedError.explanation}
        </p>
        {"stack" in parsedError && (
          <div>
            <h3 className="text-sm font-semibold text-red-700 dark:text-gray-100">
              Stack trace
            </h3>
            <pre className="mt-4 text-sm font-mono text-red-400 dark:text-red-500">
              {parsedError.stack}
            </pre>
          </div>
        )}
      </div>
      <div className="mt-8 flex flex-wrap justify-center gap-2">
        <button
          className="mx-auto block rounded bg-red-500 text-white btn btn-wide dark:bg-red-700 hover:bg-red-600 dark:hover:bg-red-800"
          onClick={resetErrorBoundary}
        >
          Try again
        </button>
        <button
          className="mx-auto block rounded bg-red-500 text-white btn btn-wide dark:bg-red-700 hover:bg-red-600 dark:hover:bg-red-800"
          onClick={() => {
            localStorage.clear();
            window.location.hash = "";
            window.location.reload();
          }}
        >
          Clear settings <br />
          and try again
        </button>
      </div>
    </div>
  );
}
