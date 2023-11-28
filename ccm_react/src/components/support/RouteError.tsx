interface FatalErrorProps {
  error: unknown;
}

function FatalError({ error }: FatalErrorProps) {
  let errorMessage: string;
  let errorStack: string | undefined;

  if (error instanceof Error) {
    errorMessage = error.message;
    errorStack = error.stack;
  } else {
    errorMessage = "Unknown error";
    errorStack = undefined;
  }

  return (
    <div className="grid h-screen place-content-center bg-white px-10">
      <h1 className="tracking-widest uppercase text-gray-500">
        <span className="text-gray-800">Fatal App Error:</span> {errorMessage}
      </h1>
      {errorStack !== undefined && (
        <details className="mt-4">
          <summary className="text-gray-500">Stack trace</summary>
          <pre className="text-gray-500">{errorStack}</pre>
        </details>
      )}
    </div>
  );
}

export default FatalError;
