import { throttle } from "lodash-es";
import { startTransition, useEffect, useState } from "react";

interface HeadingData {
  id: string;
  text: string;
  level: number;
}

export function Sidebar() {
  const [headings, setHeadings] = useState<HeadingData[]>([]);

  useEffect(() => {
    const updateHeadings = throttle(() => {
      const headingElements = Array.from(
        document.querySelectorAll(
          "main h2, main h3, main h4, main h5, main h6",
        ),
      );

      const headingData: HeadingData[] = [];
      for (const heading of headingElements) {
        if (heading.id === "" || heading.textContent === null) continue;
        const level = parseInt(heading.tagName[1], 10) - 2;
        headingData.push({
          id: heading.id,
          text: heading.textContent ?? "",
          level: level,
        });
      }

      if (JSON.stringify(headingData) !== JSON.stringify(headings)) {
        startTransition(() => {
          setHeadings(headingData);
        });
      }
    }, 500);

    const observer = new MutationObserver(() => {
      updateHeadings();
    });

    const targetElement = document.querySelector("main");

    if (targetElement) {
      observer.observe(targetElement, {
        attributes: false,
        childList: true,
        subtree: true,
        characterData: false,
      });
    }

    updateHeadings();

    return () => {
      observer.disconnect();
    };
  }, [headings]);

  function scrollToHeading(headingId: string) {
    const heading = document.getElementById(headingId);
    if (!heading) {
      console.warn(`Heading with id "${headingId}" not found.`);
      return;
    }
    heading.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <aside
      id="sidebar"
      className="sticky top-0 hidden h-fit w-1/5 overflow-auto p-8 md:block"
    >
      <p className="mb-2 text-lg font-semibold">On this page</p>
      <nav>
        <ul className="mt-0 list-none pl-0">
          {headings.map((heading) => (
            <li
              key={heading.id}
              style={{ marginLeft: `${heading.level * 0.35}em` }}
            >
              <button
                className="cursor-pointer border-none bg-transparent text-blue-900 hover:text-blue-700 hover:underline"
                onClick={() => {
                  scrollToHeading(heading.id);
                }}
              >
                {heading.text}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
