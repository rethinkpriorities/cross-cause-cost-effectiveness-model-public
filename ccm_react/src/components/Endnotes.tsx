import { useAtomValue } from "jotai";
import { FootnoteAtom } from "../stores/footnotes";
export const Endnotes = () => {
  const footnotes = useAtomValue(FootnoteAtom);
  return (
    <div className={`text-sm w-[100%]`}>
      {footnotes.length > 0 && (
        <hr className="my-8 border-2 bg-gray-200 dark:bg-gray-700" />
      )}
      {footnotes.map((v, idx) => {
        return (
          <div className="flex" key={String(v)}>
            <sup className="mr-2" id={`footnote-${idx + 1}`}>
              {idx + 1}
            </sup>
            <div>{v[1]}</div>
          </div>
        );
      })}
    </div>
  );
};
