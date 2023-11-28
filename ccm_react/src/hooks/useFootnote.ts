import { useAtomValue, useSetAtom } from "jotai";
import { useEffect } from "react";
import {
  FootnoteAtom,
  DeleteFootnoteAtom,
  AddFootnoteAtom,
} from "../stores/footnotes";

export const useFootnote = (fkey: string, node: React.ReactNode): number => {
  const footnotes = useAtomValue(FootnoteAtom);
  const deleteFootnote = useSetAtom(DeleteFootnoteAtom);
  const addFootnote = useSetAtom(AddFootnoteAtom);
  const alreadyIncluded = !footnotes.every((f) => f[0] !== fkey);
  if (!alreadyIncluded) {
    addFootnote([fkey, node]);
  }
  useEffect(() => {
    // Return function to remove the footnote once it is unmounted.
    return () => {
      deleteFootnote(fkey);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [alreadyIncluded]);
  return footnotes.findIndex((v) => v[0] === fkey) + 1;
};
