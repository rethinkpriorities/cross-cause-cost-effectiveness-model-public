import { useAtomValue } from "jotai";
import React, { useEffect } from "react";
import { Endnotes } from "../components/Endnotes";
import { ErrorBoundary } from "../components/support/ErrorHandling";
import { Sidebar } from "../components/Sidebar";
import RPLogo from "../images/rp.logo.full.png";
import { versionAtom } from "../stores/version";

export const ReportLayout = ({ children }: { children: React.ReactNode }) => {
  const version = useAtomValue(versionAtom);

  useEffect(() => {
    console.log(`Running CCM version ${version}`);
  }, [version]);

  return (
    <div>
      <div className="mx-auto max-w-screen-xl px-4 font-sans lg:px-8 sm:px-6">
        <div className="flex flex-col md:flex-row">
          <div className="min-h-screen w-4/5 p-8 pr-12">
            <header className="mb-6">
              <a
                target="_blank"
                rel="noreferrer"
                href="https://rethinkpriorities.org"
              >
                <img
                  className="mt-7 h-15 md:mt-3 md:h-12"
                  alt="Rethink Priorities Logo"
                  src={RPLogo}
                />
              </a>
              <h1 className="mb-0 mt-3 text-4xl font-semibold">
                <span className="whitespace-nowrap">Cross-Cause</span>{" "}
                <span className="sm:whitespace-nowrap">Cost-Effectiveness</span>{" "}
                Model
              </h1>
              <h4 className="mt-0 text-gray-400">Version {version}</h4>
            </header>
            <main className="prose">
              <ErrorBoundary>{children}</ErrorBoundary>
              <Endnotes />
            </main>
          </div>
          <Sidebar />
        </div>
      </div>
      <footer className="m-0 bg-[#32729100] bg-opacity-100 p-5 text-center">
        <span className="c-white">
          A project of{" "}
          <a
            target="_blank"
            rel="noreferrer"
            href="https://rethinkpriorities.org"
            className="c-white"
          >
            Rethink Priorities
          </a>{" "}
          (2023)
        </span>
      </footer>
    </div>
  );
};
