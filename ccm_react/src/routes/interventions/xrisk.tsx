import { Route } from "@tanstack/react-router";
import { xRiskInterventionsPage } from "../../pages/interventions/XRiskInterventionsPage";
import { rootRoute } from "../root";

export const interventionsXRiskRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/interventions/xrisk",
  component: xRiskInterventionsPage,
});
