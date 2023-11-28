import { Route } from "@tanstack/react-router";
import { Projects } from "../../collections/report/Projects";
import { dashboardRoute } from "../dashboard";

export const projectsRoute = new Route({
  getParentRoute: () => dashboardRoute,
  path: "/projects",
  component: Projects,
});
