import { Route } from "@tanstack/react-router";
import { rootRoute } from "./root";
import { PageNotFound } from "../pages/PageNotFound";

export const pageNotFoundRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/*",
  component: () => <PageNotFound />,
});
