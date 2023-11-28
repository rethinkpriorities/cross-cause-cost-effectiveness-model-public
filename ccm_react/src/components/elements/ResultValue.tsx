export function ResultValue({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`bg-yellow-200 dark:text-slate-700 ${className}`}
      style={{
        border: "1px solid",
        borderRadius: "4px",
        borderColor: "transparent",
      }}
    >
      {children}
    </span>
  );
}
