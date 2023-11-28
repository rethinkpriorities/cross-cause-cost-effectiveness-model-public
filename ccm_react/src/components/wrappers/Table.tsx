export const Table = ({
  children,
  name,
  caption,
}: {
  name: string;
  children: React.ReactNode;
  caption?: React.ReactNode;
}) => {
  return (
    <div className="mb-10 mt-5">
      {children}
      <div className="caption mt-5 text-sm">
        <strong>{name}.</strong> {caption}
      </div>
    </div>
  );
};
