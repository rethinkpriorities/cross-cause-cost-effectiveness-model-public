import { atom } from "jotai";

export const FootnoteAtom = atom<[string, React.ReactNode][]>([]);
export const AddFootnoteAtom = atom(
  null,
  (get, set, update: [string, React.ReactNode]) => {
    const footnotes = get(FootnoteAtom);
    footnotes.push(update);
    set(FootnoteAtom, footnotes);
  },
);
export const DeleteFootnoteAtom = atom(null, (get, set, fkey: string) => {
  let footnotes = get(FootnoteAtom);
  footnotes = footnotes.filter((f) => f[0] !== fkey);
  set(FootnoteAtom, footnotes);
});
