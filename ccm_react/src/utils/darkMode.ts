import { useEffect } from "react";

/**
 * Adds dark mode classes to the document element,
 * enabling a dark mode bg in the current page.
 * Handling cleanup when the component unmounts.
 */
export function useDarkModeBg() {
  useEffect(() => {
    document.documentElement.classList.add("bg-dashboard-light");
    document.documentElement.classList.add("dark:bg-dashboard-dark");
    return () => {
      document.documentElement.classList.remove("bg-dashboard-light");
      document.documentElement.classList.remove("dark:bg-dashboard-dark");
    };
  });
}
