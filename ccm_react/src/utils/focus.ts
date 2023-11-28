export const focusOnNextFocusable = (): void => {
  const focusable = Array.from(
    document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    ),
  ).filter((el) => !(el as HTMLElement).hidden); // Get all focusable elements

  const currentIndex = focusable.indexOf(document.activeElement!); // Get current focused element

  if (currentIndex !== -1) {
    // If there is a focused element..
    const nextIndex = (currentIndex + 1) % focusable.length; // Get next focusable element
    (focusable[nextIndex] as HTMLElement).focus(); // Set focus to next element
  }
};
