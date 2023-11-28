export interface Formatter {
  format: (value: number) => string;
}

export const predefinedFormats = {
  decimal: new Intl.NumberFormat("en-US", {
    notation: "compact",
    style: "decimal",
  }),
  preciseDecimal: new Intl.NumberFormat("en-US", {
    style: "decimal",
    maximumFractionDigits: 9,
  }),
  currency: new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 0,
  }),
  percent: new Intl.NumberFormat("en-US", {
    style: "percent",
    maximumSignificantDigits: 4,
  }),
  odds: {
    format: (value: number) => {
      // x times y
      const plural = (x: number) => (x == 1 ? "" : "s");
      return `${numberAsIntegerString(value)} time${plural(value)}`;
    },
  },
};

export type FormatType = keyof typeof predefinedFormats | "unit";

/**
 * Returns a formatter for the given type.
 * @param type Available types are: decimal, preciseDecimal, currency, percent, odds, unit
 * @param unit Available units can be found in: https://tc39.es/ecma402/#table-sanctioned-single-unit-identifiers
 * @returns formatted number as a string
 */
export function getFormat(type: FormatType, unit?: string) {
  let formatter: Intl.NumberFormat | Formatter;
  if (type != "unit") {
    formatter = predefinedFormats[type];
  } else {
    if (!unit) {
      throw new Error("Unit must be defined for type 'unit'");
    }
    formatter = new Intl.NumberFormat("en-US", {
      style: "unit",
      unit: unit,
      notation: "compact",
      unitDisplay: "long",
    });
  }
  return formatter;
}
export const numberAsDollars = (numberToFormat: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: Math.min(
      Math.max(Math.floor(Math.log10(1 / numberToFormat)) + 2, 2),
      5,
    ),
    notation: Math.abs(numberToFormat) >= 10000 ? "compact" : undefined,
    // handle negative 0.
  }).format(numberToFormat === 0 ? 0 : numberToFormat);

interface numberAsIntegerStringOptions {
  precision?: number;
  seperator?: boolean;
}
export const numberAsIntegerString = (
  numberToFormat: number,
  options: numberAsIntegerStringOptions = { seperator: true, precision: 0 },
) =>
  new Intl.NumberFormat("en-US", {
    notation: Math.abs(numberToFormat) >= 10000 ? "compact" : undefined,
    maximumFractionDigits: options.precision,
    useGrouping: options.seperator,
    // handle negative 0.
  }).format(numberToFormat === 0 ? 0 : numberToFormat);

export const numberAsDecimalString = (
  numberToFormat: number,
  options: numberAsIntegerStringOptions = {
    seperator: true,
    precision: undefined,
  },
) => {
  let defaultPrecision = Math.max(
    0,
    Math.log10(Math.floor(1 / (numberToFormat % 1))) + 2,
  );
  defaultPrecision = Math.max(0, defaultPrecision);
  defaultPrecision = Math.min(9, defaultPrecision);
  return new Intl.NumberFormat("en-US", {
    notation: Math.abs(numberToFormat) > 10000 ? "compact" : undefined,
    maximumFractionDigits: options.precision ?? defaultPrecision,
    useGrouping: options.seperator,
    // handle negative 0.
  }).format(numberToFormat === 0 ? 0 : numberToFormat);
};
