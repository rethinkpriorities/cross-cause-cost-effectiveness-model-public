import { PrimitiveAtom } from "jotai";
import { atomWithStorage } from "jotai/utils";
import type { SyncStorage } from "jotai/vanilla/utils/atomWithStorage";
import JSONCrush from "jsoncrush";
import isEqual from "lodash-es/isEqual";
interface Serializer<Value> {
  serialize: (value: Value) => string;
  deserialize: (str: string) => Value | undefined;
}

export const DefaultSerializer: Serializer<unknown> = {
  serialize: (value) => JSONCrush.crush(JSON.stringify(value)),
  deserialize: (str) => JSON.parse(JSONCrush.uncrush(str)) as unknown,
};

export function atomWithStoredHash<Value>(
  key: string,
  initialValue: Value,
  options?: {
    alwaysSave?: boolean;
    boundToPage?: boolean;
    serializer?: Serializer<Value>;
  },
): PrimitiveAtom<Value> {
  const { serializer = DefaultSerializer } = options ?? {};

  const hashStorage: SyncStorage<Value> = {
    getItem: (key, initialValue) => {
      // If this is a page-bound atom, we need to add the page to the key
      const localStorageKey = options?.boundToPage
        ? `${key}-${window.location.pathname}`
        : key;

      // Fetch the value from the URL hashes
      const searchParams = new URLSearchParams(location.hash.slice(1));
      let storedValue = searchParams.get(key);

      if (storedValue !== null) {
        // Commit new value to localStorage
        localStorage.setItem(localStorageKey, storedValue);
      } else if (
        storedValue === null &&
        localStorage.getItem(localStorageKey) !== null
      ) {
        // Rehydrate the hash from localStorage
        storedValue = localStorage.getItem(localStorageKey)!;
        searchParams.set(key, storedValue);
        location.hash = searchParams.toString();
      } else {
        // Fallback to the initial value
        if (options?.alwaysSave) {
          hashStorage.setItem(key, initialValue);
        }
        return initialValue;
      }
      try {
        return serializer.deserialize(storedValue) as Value;
      } catch (e) {
        if (e instanceof SyntaxError) {
          console.warn(
            `Failed to deserialize value when getting value of "${key}". Falling back to initial value.`,
          );
          hashStorage.removeItem(key);
          return initialValue;
        } else {
          throw e;
        }
      }
    },
    setItem: (key, newValue) => {
      // This bounds the key to the current page
      const localStorageKey = options?.boundToPage
        ? `${key}-${window.location.pathname}`
        : key;

      // If the new value is the same as its initial value
      // we remove it from storage.
      if (!options?.alwaysSave && isEqual(initialValue, newValue)) {
        hashStorage.removeItem(key);
        return;
      }

      const searchParams = new URLSearchParams(location.hash.slice(1));
      const serializedValue = serializer.serialize(newValue);

      searchParams.set(key, serializedValue);
      location.hash = searchParams.toString();
      localStorage.setItem(localStorageKey, serializedValue);
    },
    removeItem: (key) => {
      const localStorageKey = options?.boundToPage
        ? `${key}-${window.location.pathname}`
        : key;

      const searchParams = new URLSearchParams(location.hash.slice(1));
      searchParams.delete(key);
      location.hash = searchParams.toString();
      localStorage.removeItem(localStorageKey);
    },
    subscribe: (key, callback, initialValue) => {
      // Handles dynamic updates to the URL hashes
      const listener = () => {
        const localStorageKey = options?.boundToPage
          ? `${key}-${window.location.pathname}`
          : key;
        const searchParams = new URLSearchParams(location.hash.slice(1));
        const str = searchParams.get(key);
        let newStr: string;
        if (str !== null) {
          // Sync update to localStorage
          localStorage.setItem(localStorageKey, str);
          newStr = str;
        } else if (localStorage.getItem(localStorageKey) !== null) {
          // Rehydrate the hash from localStorage
          const storedValue = localStorage.getItem(localStorageKey)!;
          searchParams.set(key, storedValue);
          location.hash = searchParams.toString();
          newStr = storedValue;
        } else {
          // Fallback to the initial value
          callback(initialValue);
          return;
        }
        try {
          callback(serializer.deserialize(newStr) as Value);
        } catch (e) {
          if (e instanceof SyntaxError) {
            console.warn(
              `Failed to deserialize when propagating new value of "${key}". Falling back to initial value.`,
            );
            hashStorage.removeItem(key);
            callback(initialValue);
          } else {
            throw e;
          }
        }
      };
      // We explicitly don't listen to "storage" events because we don't want to synchronize
      // localStorage inmediately, but only when a user opens the tab and there's no hash.
      window.addEventListener("hashchange", listener);

      return () => {
        window.removeEventListener("hashchange", listener);
      };
    },
  };

  const atom = atomWithStorage(key, initialValue, hashStorage);
  atom.debugLabel = key;

  return atom;
}

export function pageSpecificAtom<Value>(
  initialValue: Value,
): PrimitiveAtom<Value> {
  return atomWithStorage(window.location.pathname, initialValue);
}
