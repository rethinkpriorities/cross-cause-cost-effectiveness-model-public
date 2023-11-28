import { useAtomValue, useSetAtom } from "jotai";
import { ResearchProjectAttributesModel } from "../../client";
import {
  availableAttributesAtom,
  baseProjectAtom,
  customAttributesAtom,
  setCustomAttributeAtom,
} from "../../stores/atoms";
import type { DistributionSpec } from "../../utils/distributions";
import { FormatType } from "../../utils/formatting";
import { ConfigurableDistribution } from "../../components/configurableDistribution/ConfigurableDistribution";

interface ConfigurableAttributeProps {
  name: keyof ResearchProjectAttributesModel;
  type?: FormatType;
  unit?: string;
}

export function ConfigurableAttribute({
  name,
  type = "decimal",
  unit,
}: ConfigurableAttributeProps) {
  const baseAttributes = useAtomValue(baseProjectAtom)
    ?.attributes as Partial<ResearchProjectAttributesModel>;
  const customAttributes = useAtomValue(customAttributesAtom);
  const attributeMeta = useAtomValue(availableAttributesAtom);
  const setAttribute = useSetAtom(setCustomAttributeAtom);
  const isModified = customAttributes[name] !== undefined;

  const baseDistribution = baseAttributes[name]!;
  const customDistribution = customAttributes[name];
  const metadata = attributeMeta[name];
  const setDistribution = (distribution: DistributionSpec | undefined) =>
    setAttribute(name, distribution);

  // Create key out of custom attributes to force re-render when they change
  const key = Object.values(customAttributes).join(",");

  return ConfigurableDistribution({
    metadata: metadata,
    customDistribution: customDistribution,
    baseDistribution: baseDistribution,
    setDistribution: setDistribution,
    isModified: isModified,
    key: key,
    type: type,
    unit: unit,
  });
}
