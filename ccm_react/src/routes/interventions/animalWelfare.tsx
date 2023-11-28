import { Route } from "@tanstack/react-router";
import { AnimalWelfareInterventionsPage } from "../../pages/interventions/AnimalWelfareInterventionsPage.tsx";
import { rootRoute } from "../root";

export const interventionsAnimalWelfareRoute = new Route({
  getParentRoute: () => rootRoute,
  path: "/interventions/animal-welfare",
  component: AnimalWelfareInterventionsPage,
});
