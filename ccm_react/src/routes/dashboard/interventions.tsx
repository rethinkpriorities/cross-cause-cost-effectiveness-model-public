import { Route } from "@tanstack/react-router";
import { Interventions } from "../../collections/report/Interventions";
import { dashboardRoute } from "../dashboard";

export const interventionsRoute = new Route({
  getParentRoute: () => dashboardRoute,
  path: "/interventions",
  component: Interventions,
});
