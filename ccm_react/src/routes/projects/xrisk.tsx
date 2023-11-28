import { Route } from "@tanstack/react-router";
import RouteError from "../../components/support/RouteError";
import { XRiskProjectsPage } from "../../pages/projects/XRiskProjectsPage";
import { rootRoute } from "../root";

export const projectsXRiskRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/projects/xrisk",
  component: XRiskProjectsPage,
  errorComponent: ({ error }) => <RouteError error={error} />,
});
