import * as BaseDialog from "@radix-ui/react-dialog";
import { Cross1Icon } from "@radix-ui/react-icons";
import { Dialog } from "@radix-ui/themes";
import { P, match } from "ts-pattern";
import { getFormat } from "../../utils/formatting";

import Markdown from "react-markdown";
import type { DistributionSpec } from "../../utils/distributions";
import { distributionMean } from "../../utils/distributions";
import { FormatType } from "../../utils/formatting";
import { DistributionPicker } from "./distributionPicker/DistributionPicker";
import { InlineButton } from "../elements/InlineButton";

export function ConfigurableDistribution({
  metadata,
  customDistribution,
  baseDistribution,
  setDistribution,
  isModified,
  key,
  type = "decimal",
  unit,
}: {
  metadata: { title: string; description: string };
  customDistribution: DistributionSpec | undefined;
  baseDistribution: DistributionSpec;
  setDistribution: (dist: DistributionSpec | undefined) => void;
  isModified: boolean;
  key: string;
  type?: FormatType;
  unit?: string;
}) {
  const formatter = getFormat(type, unit);
  const betaFormatter = ["decimal", "percent"].includes(type)
    ? Intl.NumberFormat("en-US", {
        notation: "compact",
        style: type,
        maximumSignificantDigits: 1,
      })
    : formatter;

  const distribution = customDistribution ?? baseDistribution;
  const explanation = match(distribution)
    .returnType<string>()
    .with({ range: P.array(P.number) }, (d) => {
      // Distributions which have a range
      return `between ${formatter.format(
        d.range[0] as number,
      )} and ${formatter.format(d.range[1] as number)}`;
    })
    .with(
      // Constant distributions
      { type: "constant", value: P.select() },
      (value) => `exactly ${formatter.format(value)}`,
    )
    .with(
      // Beta distributions
      { type: "beta" },
      (d) => `around ${betaFormatter.format(distributionMean(d)!)}`,
    )
    .with(
      // Gamma distributions
      { type: "gamma" },
      (d) =>
        `[value characterized by Gamma(${formatter.format(
          d.shape,
        )}, ${formatter.format(d.scale)})]`,
    )
    .with(
      // Other distributions
      // TODO(agucova): Improve using evaluated Squiggle ranges
      { type: P.select() },
      (name) => `[value characterized by a ${name} distribution]`,
    )
    .exhaustive();

  return (
    <Dialog.Root>
      <BaseDialog.Trigger asChild>
        <InlineButton isHighlighted={isModified} key={key}>
          {explanation}
        </InlineButton>
      </BaseDialog.Trigger>
      <Dialog.Content className="relative">
        <Dialog.Close>
          <button
            className="absolute right-[10px] top-[10px] h-[25px] w-[25px] inline-flex appearance-none items-center justify-center rounded-full hover:text-blue-5 focus:shadow-[0_0_0_2px] focus:outline-1 focus:outline-none"
            tabIndex={-1}
          >
            <Cross1Icon />
          </button>
        </Dialog.Close>
        <Dialog.Title>Modifying attribute: {metadata.title}</Dialog.Title>
        <Markdown>{metadata.description}</Markdown>
        <DistributionPicker
          distribution={customDistribution}
          setDistribution={setDistribution}
          baseDistribution={baseDistribution}
          type={type}
          unit={unit}
        />
      </Dialog.Content>
    </Dialog.Root>
  );
}
