import { Route } from "@tanstack/react-router";
import RouteError from "../../components/support/RouteError";
import { AnimalWelfareProjectsPage } from "../../pages/projects/AnimalWelfareProjectsPage";
import { rootRoute } from "../root";

export const projectsAnimalWelfareRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/projects/animal-welfare",
  component: AnimalWelfareProjectsPage,
  errorComponent: ({ error }) => <RouteError error={error} />,
});
