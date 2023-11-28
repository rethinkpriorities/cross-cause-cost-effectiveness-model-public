import { Route } from "@tanstack/react-router";
import { GhdProjectsPage } from "../../pages/projects/GhdProjectsPage";
import { rootRoute } from "../root";

export const projectsGHDRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/projects/ghd",
  component: GhdProjectsPage,
});
