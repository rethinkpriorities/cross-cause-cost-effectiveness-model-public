export function Introduction() {
  return (
    <section>
      <h2 id="introduction">Introduction</h2>
      <p>
        Welcome to Rethink Priorities&apos; Cross-Cause Cost-Effectiveness Model
        (CCM). The CCM is a tool that helps assess the cost-effectiveness of
        interventions and research projects by allowing one to interact with
        ready-made mathematical models with flexible assumptions. The CCM builds
        upon work made by the{" "}
        <a
          href="https://rethinkpriorities.org/news/worldview-investigation-team-introduction"
          target="_blank"
          rel="noreferrer"
        >
          Worldview Investigations Team
        </a>{" "}
        (and previously the{" "}
        <a
          href="https://rethinkpriorities.org/publications/an-introduction-to-the-moral-weight-project"
          target="_blank"
          rel="noreferrer"
        >
          Moral Weights Project
        </a>
        ) and encompasses the areas of Global Health and Development (GHD),
        Animal Welfare, and Existential Risk Mitigation.
      </p>
      <p>
        At its core, the CCM provides an interface to a collection of models
        that attempt to estimate the cost-effectiveness of projects and
        interventions while considering the uncertainty of their assumptions.
        This estimation works by running{" "}
        <a
          href="https://en.wikipedia.org/wiki/Monte_Carlo_method"
          target="_blank"
          rel="noreferrer"
        >
          Monte Carlo experiments
        </a>
        , simulating many different values which fit the assumptions, and
        aggregating the cost-effectiveness of the hypothetical intervention in
        each.
      </p>
      <p>
        The CCM is a work in progress. This is an early version of the model,
        and if you have any feedback, please{" "}
        <a
          href="https://docs.google.com/forms/d/e/1FAIpQLSdOpfNhefYhgbRb0goUKC9gS1ffydg2MLgET2OZDqDsGlsKYw/viewform"
          target="_blank"
          rel="noreferrer"
        >
          let us know
        </a>
        . We expect there could still be errors in the way we model some
        interventions, and we will be releasing a more detailed write-up in the
        following days.
      </p>
    </section>
  );
}
