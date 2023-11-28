import { atom } from "jotai";

// This really doesn't need to be an atom.
export const versionAtom = atom(
  (import.meta.env.VITE_APP_VERSION as string) ?? "?",
);
