import { Button, Callout, Flex } from "@radix-ui/themes";

export const CustomizationNote = ({
  triggerReset,
}: {
  triggerReset: () => void;
}) => {
  return (
    <Callout.Root>
      <Flex align="center">
        <Callout.Text>
          You&apos;ve modified the attributes for this intervention. The
          intervention assessment now reflects your changes.
        </Callout.Text>
        <Button
          variant="soft"
          color="crimson"
          className="min-h-10 cursor-pointer"
          onClick={triggerReset}
        >
          Reset all attributes
        </Button>
      </Flex>
    </Callout.Root>
  );
};
