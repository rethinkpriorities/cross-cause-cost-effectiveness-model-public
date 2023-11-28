## Core Model

A note on terminology: throughout the codebase and and documentation, you will see "DALY" used interchangeably with "DALY-averted". Whether a DALY or DALY-averted is being referenced is context-dependent. Unless otherwise noted, DALY figures are being reported in human-equivalent DALY terms (e.g., animal DALYs are converted to human-equivalent DALYs adjusting for relative Moral Weight).

### World

General models of aspects of the universe which may be relevant independent of any particular Intervention or Research Project,
such as Population, Risks, and Moral Weight.

### Interventions

Models of specific projects (Interventions) in different cause areas which can be invested in and which influence the world state,
measured in DALYs-per-$1000.

- GHD
- Animal Welfare
- X-Risk
  - Impact Methods: Different strategies for estimating Healthy Life Years Saved given Risk Type, Proporition of Risk Reduced, and Years Risk Reduced.

### ResearchProjects

Models for assessing Research Projects which may discover new Interventions and/or otherwise convince funders to move funding to
more effective interventions.

- Research Project
  - ROI: how many times more QALYs will be produced if money from a given Funding Pool is invested in the Research Project instead of the assumed counterfactual use of that money.
  - Gross DALYs-per-$1000: How many additional QALYs are produced for each $1000 invested in the Research Project. Ignores any counterfactual use of the Research funding money.
  - Net DALYs-per-$1000: Note that this is dependent on the assumed counterfactual use of the $1000, because in order to subtract costs from a Gross DALY amount, in order to keep units the same, we must convert the dollar costs into equivalent DALY costs (which depends on the assumed counterfactual use of the funds).
- Funding Pool: A pool of money from which funds are withdrawn, distinguished by what that money would be spent on counterfactually if a Research Project did not successfully redirect those funds to something else. The less effective the counterfactual use of funds, the 'cheaper' that money is counterfactually in DALY terms.
