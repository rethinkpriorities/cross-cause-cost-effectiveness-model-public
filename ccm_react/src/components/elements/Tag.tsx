import { FC } from "react";

interface TagProps {
  children: React.ReactNode;
  onClick: () => void;
  isSelected: boolean;
  inTwoLines?: boolean; // Optional prop to determine if the tag should span two lines
}

export const Tag: FC<TagProps> = ({
  children,
  onClick,
  isSelected,
  inTwoLines = false,
}) => (
  <button
    className={`inline-flex items-center px-3 py-1 rounded-lg shadow-sm focus:outline-none text-sm cursor-pointer ${
      isSelected
        ? "bg-dashboard-gray text-white dark:bg-white dark:text-dashboard-dark hover:bg-dashboard-gray hover:text-white dark:hover:bg-white dark:hover:text-dashboard-dark"
        : "bg-white text-dashboard-dark dark:bg-dashboard-gray dark:text-gray-200 hover:bg-dashboard-gray hover:text-white dark:hover:bg-white dark:hover:text-dashboard-dark"
    } mr-2 mb-2 ${
      inTwoLines ? "h-14 w-full flex items-center justify-center" : "h-7" // Adjust the height based on whether inTwoLines is true
    } overflow-hidden`}
    onClick={onClick}
  >
    <span className={`${inTwoLines ? "whitespace-normal" : "truncate"}`}>
      {children}
    </span>
  </button>
);
