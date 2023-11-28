/*
 * Convert to symmetric log scale, which is like a log scale except that it's
 * well-defined for zero and negative inputs. symLog(x) ~= sign(x) * log(abs(x)) for large
 * absolute values of x, and symLog(x) ~= 0 for x ~= 0. This is the same
 * function used by ObservablePlot's "symlog" plot type. For more, see J. Beau W.
 * Webber, "A Bi-Symmetric Log transformation for wide-range data."
 */
export function symLog(x: number) {
  const C = 1 / Math.log(10);
  return (Math.sign(x) * Math.log(1 + Math.abs(x / C))) / Math.log(10);
}

/* The inverse of `symLog`. */
export function symPow(y: number) {
  const C = 1 / Math.log(10);
  return Math.sign(y) * C * (-1 + Math.pow(10, Math.abs(y)));
}
