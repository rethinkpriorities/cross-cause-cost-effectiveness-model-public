/* eslint @typescript-eslint/ban-ts-comment: 0 */
/* eslint @typescript-eslint/no-unsafe-assignment: 0 */
/* eslint @typescript-eslint/no-unsafe-member-access: 0 */
import { updateParamsToLatestVersion } from "./updaters";

describe("model structure updater tests", () => {
  test("should update longterm params from v1", () => {
    const v1Params = {
      longterm_params: {
        max_creditable_year: 50000,
        stellar_population_capacity: 20,
        expansion_speed: 10,
        supercluster_density: 1,
        galactic_density: 100,
      },
    };
    const latestParams = updateParamsToLatestVersion(v1Params);
    expect(
      latestParams.longterm_params!.stellar_population_capacity?.type,
    ).toBe("constant");
    expect(
      // @ts-ignore
      latestParams.longterm_params!.stellar_population_capacity?.value,
    ).toBe(20);
    expect(latestParams.longterm_params!.expansion_speed?.type).toBe(
      "constant",
    );
    // @ts-ignore
    expect(latestParams.longterm_params!.expansion_speed?.value).toBe(10);
    expect(latestParams.longterm_params!.galactic_density?.type).toBe(
      "constant",
    );
    // @ts-ignore
    expect(latestParams.longterm_params!.galactic_density?.value).toBe(100);
    expect(latestParams.longterm_params!.supercluster_density?.type).toBe(
      "constant",
    );
    // @ts-ignore
    expect(latestParams.longterm_params!.supercluster_density?.value).toBe(1);
    expect(latestParams.longterm_params!.version).toBe("2");
  });

  test("shouldn't add keys where they're not defined", () => {
    const v1Params = {
      longterm_params: {
        max_creditable_year: 50000,
      },
    };
    const latestParams = updateParamsToLatestVersion(v1Params);
    expect(latestParams.longterm_params!.stellar_population_capacity).toBe(
      undefined,
    );
    expect(latestParams.longterm_params!.expansion_speed).toBe(undefined);
    expect(latestParams.longterm_params!.galactic_density).toBe(undefined);
    expect(latestParams.longterm_params!.supercluster_density).toBe(undefined);
    expect(latestParams.longterm_params!.version).toBe("2");
  });

  it("should handle errors gracefully", () => {
    const v1Params = {
      longterm_params: {
        max_creditable_year: 50000,
        supercluster_density: 0,
      },
    };

    // define a custom getter on v1Params to throw an error whenever it is accessed
    Object.defineProperty(v1Params.longterm_params, "supercluster_density", {
      get: function () {
        throw new Error("Cannot access supercluster_density");
      },
    });

    // verify that error is thrown
    // console.log(v1Params.longterm_params.supercluster_density); // this will throw the error
    const latestParams = updateParamsToLatestVersion(v1Params);
    expect(latestParams).not.toHaveProperty("version");
  });
});
