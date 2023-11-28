import type { SparseSamples } from "../client/models/SparseSamples";

export function sparseLength(samples: SparseSamples): number {
  return samples.samples.length + samples.num_zeros;
}

export function sparseMean(samples: SparseSamples): number {
  return (
    samples.samples.reduce((a, b) => a + b, 0) /
    (samples.samples.length + samples.num_zeros)
  );
}

/* Returns the nth element of a sorted sparse array. O(n) runtime. */
export function sparseNth(samples: SparseSamples, idx: number) {
  for (let i = 1; i < samples.samples.length; i++) {
    if (samples.samples[i - 1] > samples.samples[i]) {
      throw new Error("sparseNth: Samples must be sorted");
    }
  }
  let zeroIndex = samples.samples.findIndex((v) => v >= 0);
  if (zeroIndex == -1) zeroIndex = samples.samples.length;
  if (idx < zeroIndex) {
    return samples.samples[idx];
  } else if (idx < zeroIndex + samples.num_zeros) {
    return 0;
  } else {
    return samples.samples[idx - samples.num_zeros];
  }
}

/* Returns the median of a sorted sparse array. */
export function sparseMedian(samples: SparseSamples): number {
  return sparseNth(samples, Math.floor(sparseLength(samples) / 2));
}
