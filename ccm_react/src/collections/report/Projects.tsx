import { ResearchProjectInteractive } from "../projects/ResearchProject";

export function Projects() {
  return (
    <section>
      <h2 id="projects">Research Projects</h2>
      <p>
        Many things we care about funding are not directly intervening in the
        world but instead performing research to improve existing interventions
        or to find better interventions. Rethink Priorities&apos; work falls
        into this category. Much of what we do has the ultimate goal of
        influencing funders to use their money more effectively.
      </p>
      <p>
        Based on the model explained in{" "}
        <a
          href="https://forum.effectivealtruism.org/posts/RQzieJvu6Ecmgagbp/a-model-estimating-the-value-of-research-influencing-funders"
          rel="noreferrer"
          target="_blank"
        >
          A Model Estimating the Value of Research Influencing Funders
        </a>
        , this part of the CCM allows you to simulate the effect of research
        projects. You can build upon the interventions shown previously or
        supply before and after cost-effectiveness estimates directly.
      </p>
      <p>
        We&apos;ve made some templates for research projects you can use as a
        starting point for your own simulations:
      </p>
      <ResearchProjectInteractive group="all" />
    </section>
  );
}
