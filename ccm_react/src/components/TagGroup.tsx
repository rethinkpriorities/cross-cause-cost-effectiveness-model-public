import { FC, useState } from "react";
import { Tag } from "./elements/Tag";
import * as CollapsiblePrimitive from "@radix-ui/react-collapsible";

const Collapsible = CollapsiblePrimitive.Root;
const CollapsibleTrigger = CollapsiblePrimitive.Trigger;
const CollapsibleContent = CollapsiblePrimitive.Content;

interface TagGroupProps {
  title: string;
  tags: TagData[];
  selectedTagId: string | null;
  onTagClick: (tag: string) => void;
  initiallyVisibleTags?: number; // TODO(agucova): Adjust according to the screen size
  inTwoLines?: boolean;
}

interface TagData {
  name: string;
  id: string;
}

export const TagGroup: FC<TagGroupProps> = ({
  title,
  tags,
  selectedTagId,
  onTagClick,
  initiallyVisibleTags = 12,
  inTwoLines = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const hiddenTagsCount = tags.length - initiallyVisibleTags;

  return (
    <div className="flex flex-col">
      <h3 className="my-0 mb-2 font-semibold dark:text-white">{title}</h3>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className="flex flex-wrap">
          {tags.slice(0, initiallyVisibleTags).map((tag) => (
            <Tag
              key={tag.id}
              onClick={() => onTagClick(tag.id)}
              isSelected={selectedTagId === tag.id}
              inTwoLines={inTwoLines}
            >
              {tag.name}
            </Tag>
          ))}
        </div>
        {hiddenTagsCount > 0 && (
          <>
            <CollapsibleContent>
              <div className="flex flex-wrap">
                {tags.slice(initiallyVisibleTags).map((tag) => (
                  <Tag
                    key={tag.id}
                    onClick={() => onTagClick(tag.id)}
                    isSelected={selectedTagId === tag.id}
                    inTwoLines={inTwoLines}
                  >
                    {tag.name}
                  </Tag>
                ))}
              </div>
            </CollapsibleContent>
            <CollapsibleTrigger className="mt-1 cursor-pointer text-sm font-semibold dark:text-white hover:underline">
              {isOpen ? "Show less" : `Show ${hiddenTagsCount} more`}
            </CollapsibleTrigger>
          </>
        )}
      </Collapsible>
    </div>
  );
};
