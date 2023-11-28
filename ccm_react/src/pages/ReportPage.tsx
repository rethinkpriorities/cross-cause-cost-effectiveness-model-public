import { Interventions } from "../collections/report/Interventions";
import { Introduction } from "../collections/report/Introduction";
import { Projects } from "../collections/report/Projects";
import { ReportLayout } from "../layouts/ReportLayout";

export const ReportPage = () => (
  <ReportLayout>
    <>
      <Introduction />
      <Interventions />
      <Projects />
    </>
  </ReportLayout>
);
