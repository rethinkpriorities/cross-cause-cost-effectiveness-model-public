import { Navigate } from "@tanstack/react-router";
import React from "react";

export const PageNotFound: React.FC = () => {
  const { location } = window;

  if (location.pathname.includes("_")) {
    const newLocation = location.pathname.replace(/_/g, "-");
    const search = location.search;
    // Navigate throwing weird typscript errors looking for 'search' key, but it works fine and is in line with docs.
    // eslint-disable-next-line
    // @ts-ignore
    return <Navigate to={newLocation + search} />;
  }

  return <div>Page Not Found</div>;
};

export default PageNotFound;
