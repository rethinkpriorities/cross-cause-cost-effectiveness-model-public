"""Repository/Factory for getting/constructing Intervention objects."""
# ruff: noqa: E501

from typing import TYPE_CHECKING

import squigglepy as sq
from squigglepy.numbers import K

import ccm.config as config
from ccm.interventions.ghd.ghd_interventions import (
    GD_COST_EFFECTIVENESS,
    GW_COST_EFFECTIVENESS,
    OP_COST_EFFECTIVENESS,
    GhdIntervention,
)
from ccm.interventions.intervention import ResultIntervention
from ccm.utility.models import ConfidenceDistributionSpec, DistributionSpec

if TYPE_CHECKING:
    from ccm.interventions.intervention_definitions.all_interventions import SomeIntervention

SIMULATIONS = config.get_simulations()


# Note: If you change the name of an Intervention here, also change it in data/projects/projects.csv

PREAMBLE_FOR_BARS = """
          This intervention models the cost-effectiveness of a hypothetical intervention that meets a
          funding bar almost exactly.
"""


def op_bar() -> GhdIntervention:
    return GhdIntervention(
        name="Open Philanthropy Bar",
        description=PREAMBLE_FOR_BARS
        + """
          Open Philanthropy aims to fund Global Health and Development projects
          that meet a [funding bar](https://www.openphilanthropy.org/research/our-planned-allocation-to-givewells-recommendations-for-the-next-few-years/#our-higher-bar-for-global-health-and-wellbeing-giving) of producing more than 2000 &times; the value of cash given to someone making $50,000 per year (their unit of value).

          Based on [their assumptions](https://www.openphilanthropy.org/research/technical-updates-to-our-global-health-and-wellbeing-cause-prioritization-framework/#3-new-moral-weights)
          about the value of a DALY (at $100K), this works out to a cost per DALY averted of around $50.
          """,
        cost_per_daly=OP_COST_EFFECTIVENESS,
    )


def gw_bar() -> GhdIntervention:
    return GhdIntervention(
        name="GiveWell Bar",
        description=PREAMBLE_FOR_BARS
        + """
          GiveWell aims to use its funding for projects with a cost per DALY of
          $56 or better. We assume that it more or less meet this aim, though
          there is some uncertainty and some funded projects will exceed this
          threshold, while others will fall short. We represent the
          effectiveness of a project meeting the GiveWell bar as a distribution
          centered at their estimate.
          """,
        cost_per_daly=GW_COST_EFFECTIVENESS,
    )


def gd_bar() -> GhdIntervention:
    return GhdIntervention(
        name="Direct Cash Transfers",
        description="""
        This is a reference intervention modelled after
        [GiveDirectly's cash transfer programs](https://www.givedirectly.org/large-transfer/),
        [as assessed by GiveWell](https://docs.google.com/spreadsheets/d/18ROI6dRdKsNfXg5gIyBa1_7eYOjowfbw5n65zkrLnvc/edit?usp=sharing).
        GiveWell's estimates were converted to dollars per DALY as [shown here](https://docs.google.com/spreadsheets/d/1Gore0LEuBBG8tM7F3phxaYPfGaYYl40eUEldtV196lU/edit?usp=sharing). We adopt a (mostly arbitrary) uncertainty distribution around this central estimate.
        """,
        cost_per_daly=GD_COST_EFFECTIVENESS,
    )


def good_ghd() -> GhdIntervention:
    """Centered on $67 / DALY"""
    return GhdIntervention(
        name="Good GHD Intervention",
        description="""
        This intervention describes a hypothetical intervention that is
        cost-effective by both Open Philanthropy's and GiveWell's standards.
        """,
        cost_per_daly=ConfidenceDistributionSpec.lognorm(15, 50),
    )


def weak_ghd() -> GhdIntervention:
    """Centered on $1000 / DALY"""
    return GhdIntervention(
        name="Weak GHD Intervention",
        description="""
        This intervention describes a hypothetical intervention that has
        a relatively weak cost-effectiveness, centered at around $1000 / DALY averted.
        """,
        cost_per_daly=ConfidenceDistributionSpec.norm(820, 1180),
    )


def standard_hiv() -> GhdIntervention:
    return GhdIntervention(
        name="Standard HIV Intervention",
        description="""
        This intervention is modelled after a typical intervention aimed at preventing
        HIV like Treatment as Prevention (TasP). The median value of this intervention
        ($900 / DALY averted) was based on this [systematic review](https://doi.org/10.1016/j.eclinm.2019.04.006).
        """,
        cost_per_daly=ConfidenceDistributionSpec.norm(800, 1100, credibility=80),
    )


def best_hiv() -> GhdIntervention:
    return GhdIntervention(
        name="Best HIV Intervention",
        description="""
        This intervention is modelled after a very cost-effective HIV intervention,
        like a particularly good mother-to-child transmission prevention program.
        The median value of this intervention ($200 / DALY averted) was based on
        [this systematic review](https://doi.org/10.1016/j.eclinm.2019.04.006).
        """,
        cost_per_daly=ConfidenceDistributionSpec.norm(150, 250, credibility=80),
    )


def ineffective_ghd() -> GhdIntervention:
    """Centered on $25,000 / DALY"""
    return GhdIntervention(
        name="Ineffective GHD Intervention",
        description="""
        This intervention describes a hypothetical intervention that is
        significantly ineffective with respect to other GHD interventions, with a cost-effectiveness
        centered on $25,000 / DALY averted.
        """,
        cost_per_daly=ConfidenceDistributionSpec.norm(18.7 * K, 31.25 * K),
    )


def very_ineffective_ghd() -> GhdIntervention:
    """Centered on $50,000 / DALY"""
    return GhdIntervention(
        name="Very Ineffective GHD Intervention",
        description="""
        This intervention describes a hypothetical intervention that is
        very ineffective with respect to other GHD interventions. The cost-effectiveness
        is centered on $50,000 / DALY averted.
        """,
        cost_per_daly=ConfidenceDistributionSpec.norm(37.5 * K, 62.5 * K),
    )


def us_government_ghd() -> GhdIntervention:
    """Centered on $1000 / DALY"""
    return GhdIntervention(
        name="US Gov GHD Intervention",
        description="""
        This intervention describes an typical health intervention funded by the US government, with a
        cost-effectiveness centered centered on $1000 / DALY averted.
        """,
        cost_per_daly=ConfidenceDistributionSpec.norm(820, 1180),
    )


def rp_research_projects():
    return ResultIntervention(
        type="result",
        area="not-an-intervention",
        name="RP Research Projects",
        description="""
        Marginal efficiency of RP Research Projects (not an actual intervention).
        """,
        result_distribution=DistributionSpec.from_sq(sq.norm(0.2, 100)),
    )


def non_impactful():
    return ResultIntervention(
        type="result",
        area="utility",
        name="Non-Impactful Spending",
        result_distribution=DistributionSpec.from_sq(sq.discrete({0.0: 1.0})),
        description="A hypothetical intervention with zero impact, or no intervention at all (e.g. burning money).",
    )


DEFAULT_INTERVENTIONS: list["SomeIntervention"] = [
    op_bar(),
    gw_bar(),
    gd_bar(),
    good_ghd(),
    weak_ghd(),
    standard_hiv(),
    best_hiv(),
    ineffective_ghd(),
    very_ineffective_ghd(),
    us_government_ghd(),
    rp_research_projects(),
    non_impactful(),
]


def get_hardcoded_interventions() -> list["SomeIntervention"]:
    return DEFAULT_INTERVENTIONS
