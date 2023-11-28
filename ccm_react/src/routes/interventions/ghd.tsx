import { Route } from "@tanstack/react-router";
import { ghdInterventionsPage } from "../../pages/interventions/GhdInterventionsPage";
import { rootRoute } from "../root";

export const interventionsGHDRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/interventions/ghd",
  component: ghdInterventionsPage,
});
