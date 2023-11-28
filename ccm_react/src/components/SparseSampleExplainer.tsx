import type { SparseSamples } from "../client/models/SparseSamples";
import { Footnote } from "./elements/Footnote";

export function SparseSampleExplainer({ samples }: { samples: SparseSamples }) {
  if (samples.num_zeros > 0) {
    return (
      <Footnote fkey="nsim">
        The samples include {samples.samples.length} true simulations and{" "}
        {samples.num_zeros} virtual simulations. It was known in advance that at
        least{" "}
        {Math.round(
          (1e4 * 100 * samples.num_zeros) /
            (samples.samples.length + samples.num_zeros),
        ) / 1e4}
        % of the simulations would have no effect, so the samples were filled
        with {samples.num_zeros} zero values as if we had run those simulations,
        and only {samples.samples.length} simulations were actually run.
      </Footnote>
    );
  } else {
    return null;
  }
}
