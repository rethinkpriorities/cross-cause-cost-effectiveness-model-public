import { Outlet, RootRoute } from "@tanstack/react-router";
import FatalError from "../components/support/RouteError";

export const rootRoute = new RootRoute({
  component: () => (
    <>
      <Outlet />
    </>
  ),
  errorComponent: FatalError,
});
