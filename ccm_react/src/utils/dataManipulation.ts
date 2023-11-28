import { mean as d3mean, format, max, min } from "d3";

// Borrowed from Jason Davies science library https://github.com/jasondavies/science.js/blob/master/science.v1.js
export function variance(x: number[]): number | undefined {
  const n = x.length;
  if (n < 1) return NaN;
  if (n === 1) return 0;
  const mean = d3mean(x);
  if (mean === undefined) return undefined;
  let i = -1,
    s = 0;
  while (++i < n) {
    const v = x[i] - mean;
    s += v * v;
  }
  return s / (n - 1);
}

// https://gist.github.com/phil-pedruco/6917114
export function chauvenetFilter(
  x: number[],
  dMax: number,
): number[] | undefined {
  const mean = d3mean(x);
  if (mean === undefined) return undefined;
  const svar = variance(x);
  if (svar === undefined) return undefined;

  const stdv = Math.sqrt(svar);
  const temp = [];

  for (const xi of x) {
    if (dMax > Math.abs(xi - mean) / stdv) {
      temp.push(xi);
    }
  }

  return temp;
}

export function chauvenetRange(
  x: number[],
  dMax: number,
): [number, number] | undefined {
  const filtered = chauvenetFilter(x, dMax);
  if (filtered === undefined) return undefined;
  return [min(filtered)!, max(filtered)!];
}

export function stdDevRange(
  x: number[],
  dMax: number,
): [number, number] | undefined {
  const mean = d3mean(x);
  if (mean === undefined) return undefined;
  const svar = variance(x);
  if (svar === undefined) return undefined;

  const stdv = Math.sqrt(svar);
  return [mean - dMax * stdv, mean + dMax * stdv];
}

type ValueOf<T> = T[keyof T];
type Entries<T> = [keyof T, ValueOf<T>][];

function objectEntries<T extends object>(obj: T): Entries<T> {
  return Object.entries(obj) as Entries<T>;
}

export function normalizeRecords<Type extends string | number | symbol>(
  records: Record<Type, number | undefined>,
): Record<Type, number | undefined> {
  // Undefined values are ignored for the purpose of normalization
  const undefinedRecords = objectEntries(records).filter(
    ([, value]) => value === undefined,
  );
  const definedRecords = objectEntries(records).filter(
    ([, value]) => value !== undefined,
  );
  // If all values are undefined, return the original object
  if (definedRecords.length === 0) return records;
  // Normalize
  const sum = definedRecords.reduce((acc, [, value]) => acc + value!, 0);
  const normalizedEntries = definedRecords.map(([key, value]) => [
    key,
    value! / sum,
  ]);
  // Combine with undefined keys
  const normalizedRecords = Object.fromEntries(normalizedEntries) as Record<
    Type,
    number
  >;
  const normalizedUndefinedRecords = Object.fromEntries(
    undefinedRecords,
  ) as Record<Type, undefined>;
  return { ...normalizedRecords, ...normalizedUndefinedRecords };
}

const number_format = format("s");

export function formatNumber(value: number | undefined): string {
  if (value === undefined) return "";
  return number_format(value);
}
