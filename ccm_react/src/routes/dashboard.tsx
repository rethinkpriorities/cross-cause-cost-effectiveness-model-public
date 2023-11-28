import { Route } from "@tanstack/react-router";
import { DashboardPage } from "../pages/DashboardPage";
import { rootRoute } from "./root";

export const dashboardRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/dashboard",
  component: DashboardPage,
});
