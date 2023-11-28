import { ClipLoader } from "react-spinners";

export function LoadingFallback({ height }: { height?: string }) {
  return (
    <div
      className="h-full w-full flex items-center justify-center"
      style={{ minHeight: height ?? "10rem" }}
    >
      <ClipLoader color="#00000" />
    </div>
  );
}
