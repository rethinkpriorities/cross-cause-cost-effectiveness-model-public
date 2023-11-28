import { useFootnote } from "../../hooks/useFootnote";

export const Footnote = ({
  fkey,
  children,
}: {
  fkey: string;
  children: React.ReactNode;
}) => {
  const num = useFootnote(fkey, children);
  return (
    <sup
      role="presentation"
      className="cursor-pointer"
      onClick={() => {
        document.getElementById(`footnote-${num}`)?.scrollIntoView();
      }}
      onKeyPress={(_e) => {
        document.getElementById(`footnote-${num}`)?.scrollIntoView();
      }}
    >
      {num}
    </sup>
  );
};
