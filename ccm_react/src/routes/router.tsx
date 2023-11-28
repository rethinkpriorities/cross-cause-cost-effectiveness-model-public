import { Router } from "@tanstack/react-router";
import { indexRoute } from "./";
import { pageNotFoundRoute } from "./404";
import { dashboardRoute } from "./dashboard";
import { interventionsRoute } from "./dashboard/interventions";
import { projectsRoute } from "./dashboard/projects";
import { interventionsAnimalWelfareRoute } from "./interventions/animalWelfare";
import { interventionsGHDRoute } from "./interventions/ghd";
import { interventionsXRiskRoute } from "./interventions/xrisk";
import { projectsAnimalWelfareRoute } from "./projects/animalWelfare";
import { projectsGHDRoute } from "./projects/ghd";
import { projectsXRiskRoute } from "./projects/xrisk";
import { rootRoute } from "./root";

// Create the route tree using your routes
const routeTree = rootRoute.addChildren([
  indexRoute,
  dashboardRoute,
  interventionsRoute,
  projectsRoute,
  interventionsGHDRoute,
  interventionsAnimalWelfareRoute,
  interventionsXRiskRoute,
  projectsGHDRoute,
  projectsAnimalWelfareRoute,
  projectsXRiskRoute,
  pageNotFoundRoute,
]);

// Create a router instance
const router = new Router({
  routeTree,
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

export default router;
