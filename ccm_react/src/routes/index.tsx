import { Route } from "@tanstack/react-router";
import { ReportPage } from "../pages/ReportPage";
import { rootRoute } from "./root";

export const indexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/",
  component: ReportPage,
});
