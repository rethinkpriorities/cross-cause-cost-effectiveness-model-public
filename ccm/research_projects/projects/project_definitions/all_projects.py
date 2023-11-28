from ccm.research_projects.projects.project_definitions.animal_welfare_projects import get_animal_projects
from ccm.research_projects.projects.project_definitions.ghd_projects import get_ghd_projects
from ccm.research_projects.projects.project_definitions.legacy_projects import get_legacy_projects
from ccm.research_projects.projects.project_definitions.xrisk_projects import get_xrisk_projects
from ccm.research_projects.projects.research_project import ResearchProject


def get_all_projects(equal_money_for_causes: bool) -> list[ResearchProject]:
    research_projects = []
    research_projects.extend(get_legacy_projects(equal_money_for_causes))
    research_projects.extend(get_ghd_projects())
    research_projects.extend(get_animal_projects())
    research_projects.extend(get_xrisk_projects())
    return research_projects
