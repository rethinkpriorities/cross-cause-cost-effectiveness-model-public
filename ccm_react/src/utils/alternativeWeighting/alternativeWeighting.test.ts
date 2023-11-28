import {
  calculateEV,
  calculateEV99,
  calculateEV99_9,
  calculateREU03,
  calculateREU05,
  calculateREU10,
  calculateWLU03,
  calculateWLU05,
  calculateWLU10,
} from "./alternativeWeighting";

describe("EV truncation tests", () => {
  test("should remove extreme values", () => {
    const values = new Array(1000).fill(1) as number[];
    values[0] = -1000;
    values[1] = -1;
    values.fill(3, 997, 999);
    values[999] = 100000;
    expect(calculateEV99(values)).toBe(1);
    expect(calculateEV99_9(values)).toBeGreaterThan(1);
    expect(calculateEV99_9(values)).toBeLessThan(3);
    expect(calculateEV(values)).toBeGreaterThan(3);
  });
});

describe("EV sparse samples tests", () => {
  const values = new Array(1000).fill(1) as number[];
  values[0] = -1000;
  values[1] = -1;
  values.fill(3, 997, 999);
  values[999] = 100000;

  for (const { name, func } of [
    { name: "EV", func: calculateEV },
    { name: "EV99", func: calculateEV99 },
    { name: "EV99.9", func: calculateEV99_9 },
  ]) {
    test(name + " with no zeros should be unchanged", () => {
      const sparseSamples = {
        samples: values,
        num_zeros: 0,
      };
      expect(func(sparseSamples)).toBe(func(values));
    });
  }

  test("EV with 9,000 zeros should be 10x smaller", () => {
    const sparseSamples = {
      samples: values,
      num_zeros: 9000,
    };
    expect(calculateEV(sparseSamples)).toBe(calculateEV(values) / 10);
  });

  test("EV99 with 9,000 zeros should cut off both tails", () => {
    const sparseSamples = {
      samples: values,
      num_zeros: 9000,
    };
    // we drop the two negative values from the left plus 50 positive from the
    // right, leaving 1000 - 2 - 50 ones
    expect(calculateEV99(sparseSamples)).toBeCloseTo(
      (1000 - 2 - 50) / 9900,
      10,
    );
  });

  test("EV99.9 with 1000 zeros should cut off one value on both sides", () => {
    const sparseSamples = {
      samples: values,
      num_zeros: 1000,
    };
    expect(calculateEV99_9(sparseSamples)).toBeCloseTo(
      (calculateEV(values.slice(1, 999)) * 998) / 999 / 2,
      10,
    );
  });

  for (const { name, func } of [
    { name: "EV", func: calculateEV },
    { name: "EV99", func: calculateEV99 },
    { name: "EV99.9", func: calculateEV99_9 },
  ]) {
    for (const { position, values } of [
      { position: "beginning", values: Array(1000).fill(1) },
      { position: "left 1%", values: Array(1000).fill(1).fill(-1, 0, 3) },
      { position: "middle", values: Array(1000).fill(1).fill(-1, 0, 500) },
      { position: "right 1%", values: Array(1000).fill(-1).fill(1, 998, 1000) },
      { position: "end", values: Array(1000).fill(-1) },
    ]) {
      test(
        name +
          " with 1000 zeros at the " +
          position +
          " should be the same for sparse zeros or for inserted dense zeros",
        () => {
          const sparseSamples = {
            samples: [...(values as number[])],
            num_zeros: 1000,
          };
          values.splice(1000, 0, ...(new Array(1000).fill(0) as number[]));
          expect(func(sparseSamples)).toBeCloseTo(func(values), 10);
        },
      );
    }
  }
});

describe("REU tests", () => {
  test("Constants should be unchanged", () => {
    expect(calculateREU03([8])).toBe(8);
    expect(calculateREU05([8])).toBe(8);
    expect(calculateREU10([8])).toBe(8);
  });
  test("Risky prospects should be discounted", () => {
    expect(calculateREU03([0, 0, 8])).toBeLessThan(8 / 3);
    expect(calculateREU05([0, 0, 8])).toBeLessThan(8 / 3);
    expect(calculateREU10([0, 0, 8])).toBeLessThan(8 / 3);
  });
  test("Risky prospects should be above minimum", () => {
    expect(calculateREU03([0, 0, 8])).toBeGreaterThan(0);
    expect(calculateREU05([0, 0, 8])).toBeGreaterThan(0);
    expect(calculateREU10([0, 0, 8])).toBeGreaterThan(0);
  });
  test("Risky prospects should be sensitive to probabilities", () => {
    expect(calculateREU03([0, 0, 8])).toBeGreaterThan(
      calculateREU03([0, 0, 0, 8]),
    );
    expect(calculateREU05([0, 0, 8])).toBeGreaterThan(
      calculateREU05([0, 0, 0, 8]),
    );
    expect(calculateREU10([0, 0, 8])).toBeGreaterThan(
      calculateREU10([0, 0, 0, 8]),
    );
  });
  test("Risky prospects should value 10 vs 1000 appropiately", () => {
    // Weighting should render equivalent an x% chance of 1000 vs 10 for certain
    // x = 3
    const percent3 = new Array(100).fill(0).fill(1000, 0, 3) as number[];
    expect(calculateREU03(percent3)).toBeCloseTo(10, 0);
    // x = 5
    const percent5 = new Array(100).fill(0).fill(1000, 0, 5) as number[];
    expect(calculateREU05(percent5)).toBeCloseTo(10, 0);
    // x = 10
    const percent10 = new Array(100).fill(0).fill(1000, 0, 10) as number[];
    expect(calculateREU10(percent10)).toBeCloseTo(10, 0);
  });
});

describe("REU sparse samples tests", () => {
  test("Adding sparse zeros at the beginning should have the same effect as adding dense zeros", () => {
    expect(
      calculateREU03({
        samples: [0, 8],
        num_zeros: 0,
      }),
    ).toBe(calculateREU03([0, 8]));
    expect(
      calculateREU03({
        samples: [8],
        num_zeros: 3,
      }),
    ).toBe(calculateREU03([0, 0, 0, 8]));
    expect(
      calculateREU03({
        samples: [0, 0, 8],
        num_zeros: 2,
      }),
    ).toBe(calculateREU03([0, 0, 0, 0, 8]));
  });
  test("Adding sparse zeros at the end should have the same effect as adding dense zeros", () => {
    expect(
      calculateREU03({
        samples: [-8],
        num_zeros: 2,
      }),
    ).toBe(calculateREU03([-8, 0, 0]));
    expect(
      calculateREU03({
        samples: [-8, 0, 0],
        num_zeros: 1,
      }),
    ).toBe(calculateREU03([-8, 0, 0, 0]));
  });
  test("Adding sparse zeros in the middle should have the same effect as adding dense zeros", () => {
    expect(
      calculateREU03({
        samples: [-4, 2, 5],
        num_zeros: 2,
      }),
    ).toBe(calculateREU03([0, 0, -4, 2, 5]));
    expect(
      calculateREU03({
        samples: [0, 0, -4, 6],
        num_zeros: 3,
      }),
    ).toBe(calculateREU03([-4, 0, 0, 0, 0, 0, 6]));
  });
});

describe("WLU tests", () => {
  test("Constants should be unchanged", () => {
    expect(calculateWLU03([8])).toBe(8);
    expect(calculateWLU05([8])).toBe(8);
    expect(calculateWLU10([8])).toBe(8);
  });
  test("Risky prospects should be discounted", () => {
    expect(calculateWLU03([0, 0, 8])).toBeLessThan(8 / 3);
    expect(calculateWLU05([0, 0, 8])).toBeLessThan(8 / 3);
    expect(calculateWLU10([0, 0, 8])).toBeLessThan(8 / 3);
  });
  test("Risky prospects should be above minimum", () => {
    expect(calculateWLU03([0, 0, 8])).toBeGreaterThan(0);
    expect(calculateWLU05([0, 0, 8])).toBeGreaterThan(0);
    expect(calculateWLU10([0, 0, 8])).toBeGreaterThan(0);
  });
  test("Risky prospects should be sensitive to probabilities", () => {
    expect(calculateWLU03([0, 0, 8])).toBeGreaterThan(
      calculateWLU03([0, 0, 0, 8]),
    );
    expect(calculateWLU05([0, 0, 8])).toBeGreaterThan(
      calculateWLU05([0, 0, 0, 8]),
    );
    expect(calculateWLU10([0, 0, 8])).toBeGreaterThan(
      calculateWLU10([0, 0, 0, 8]),
    );
  });
  test("Risky prospects should value 10 vs 1000 appropiately", () => {
    // Weighting should render equivalent an x% chance of 1000 vs 10 for certain
    // x = 3
    const percent3 = new Array(100).fill(0).fill(1000, 0, 3) as number[];
    expect(calculateWLU03(percent3)).toBeCloseTo(10, 0);
    // x = 5
    const percent5 = new Array(100).fill(0).fill(1000, 0, 5) as number[];
    expect(calculateWLU05(percent5)).toBeCloseTo(10, 0);
    // x = 10
    const percent10 = new Array(100).fill(0).fill(1000, 0, 10) as number[];
    expect(calculateWLU10(percent10)).toBeCloseTo(10, 0);
  });
});

describe("WLU sparse samples tests", () => {
  test("Risky prospects with no zeros should be unchanged", () => {
    expect(
      calculateWLU03({
        samples: [0, 0, 8],
        num_zeros: 0,
      }),
    ).toBe(calculateWLU03([0, 0, 8]));
  });
  test("Adding sparse zeros should have the same effect as adding dense zeros", () => {
    expect(
      calculateWLU03({
        samples: [8],
        num_zeros: 3,
      }),
    ).toBe(calculateWLU03([0, 0, 0, 8]));
    expect(
      calculateWLU03({
        samples: [0, 0, 8],
        num_zeros: 2,
      }),
    ).toBe(calculateWLU03([0, 0, 0, 0, 8]));
  });
});
