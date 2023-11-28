import { useAtom } from "jotai";
import { atomWithStorage } from "jotai/utils";

import { Callout, Flex } from "@radix-ui/themes";
import { Cross1Icon } from "@radix-ui/react-icons";
import { ResultValue } from "./elements/ResultValue";
import { InlineButton } from "./elements/InlineButton";

const showConfigurabilityMessage = atomWithStorage(
  "showConfigurabilityMessage",
  false,
);

export const ConfigurabilityMessage = () => {
  const [shouldHide, setShouldHide] = useAtom(showConfigurabilityMessage);
  if (shouldHide) return null;
  return (
    <Flex direction="row" gap="3" justify="center" className="mb-10 mt-10">
      <Callout.Root
        size="2"
        color="yellow"
        highContrast={true}
        variant="outline"
      >
        <Callout.Text className="ml-5" as="div">
          You can modify highlighted text by clicking on it.
          <ul className="w-full list-none p-0">
            {" "}
            <li>
              <InlineButton>Blue highlighting</InlineButton> indicates a{" "}
              <strong>default parameter</strong>.
            </li>
            <li>
              <InlineButton isHighlighted={true}>
                Orange highlighting
              </InlineButton>{" "}
              indicates a parameter that <strong>you have modified</strong>.
            </li>
            <li>
              <ResultValue>Yellow highlighting</ResultValue> indicates a{" "}
              <strong>computed value</strong> that you{" "}
              <strong>cannot change directly</strong>, but it changes when you
              modify other parameters.
            </li>
          </ul>
        </Callout.Text>
        <Callout.Icon
          className="cursor-pointer"
          onClick={() => setShouldHide(true)}
        >
          <Cross1Icon height="1em" width="1em" />
        </Callout.Icon>
      </Callout.Root>
    </Flex>
  );
};
