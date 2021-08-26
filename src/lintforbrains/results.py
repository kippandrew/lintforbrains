import enum
import os
import pathlib
import typing

from lxml import etree

import lintforbrains.config
import lintforbrains.logging

from lintforbrains.utilities import substitute

__all__ = [
    'latest_results_dir',
    'InspectionResults',
    'InspectionProblem',
    'InspectionProblemSeverity',
    'InspectionProfile',
    'InspectionGroup',
    'InspectionType',
]

_LOG = lintforbrains.logging.get_logger(__name__)


def latest_results_dir(project_dir: str, configuration: lintforbrains.config.Configuration):
    results_dir = os.path.normpath(os.path.join(project_dir, configuration.inspect.results_dir))

    most_recent_results_time = None
    most_recent_results_dir = None
    for p in pathlib.Path(results_dir).iterdir():
        if p.is_dir():
            st = p.stat()
            if most_recent_results_time is None or st.st_mtime > most_recent_results_time:
                most_recent_results_time = st.st_mtime
                most_recent_results_dir = os.path.normpath(os.path.join(results_dir, p.name))

    if most_recent_results_dir is not None:
        _LOG.debug(f"Found most recent inspection results {most_recent_results_dir}")

    return most_recent_results_dir


class InspectionProfile:
    """
    TODO: needs class summary
    """

    groups: typing.MutableMapping[str, 'InspectionGroup']

    def __init__(self, profile_name: str):
        """
        Initialize instance of the InspectionProfile class.

        :param profile_name: inspection profile name
        """
        self.name = profile_name
        self.groups = dict()


class InspectionGroup:
    """
    TODO: needs class summary
    """
    inspections: typing.MutableMapping[str, 'InspectionType']

    def __init__(self, profile: InspectionProfile, group_name: str):
        """
        Initialize instance of the InspectionGroup class.

        :param profile: parent inspection profile
        :param group_name: inspection group name
        """
        self.profile = profile
        self.name = group_name
        self.inspections = dict()

        self.profile.groups[group_name] = self

    def __lt__(self, other):
        if isinstance(other, InspectionGroup):
            return self.name < other.name
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, InspectionGroup):
            return (self.profile == other.profile and
                    self.name == other.name)
        else:
            return NotImplemented

    def __str__(self):
        return f"InspectionGroup ({self.name})"


class InspectionType:
    """
    TODO: needs class summary
    """

    group: InspectionGroup

    def __init__(self,
                 group: InspectionGroup,
                 inspection_name: str,
                 inspection_title: str,
                 inspection_description: str,
                 inspection_enabled: bool):
        """
        Initialize instance of the InspectionType class.

        :param group: parent inspection group
        :param inspection_name: inspection rule name
        :param inspection_title: inspection rule title
        :param inspection_description: inspection rule description (html)
        :param inspection_enabled: inspection rule enabled
        """
        self.group = group
        self.name = inspection_name
        self.title = inspection_title
        self.description = inspection_description
        self.enabled = inspection_enabled

        self.group.inspections[inspection_name] = self

    def __lt__(self, other):
        if isinstance(other, InspectionType):
            return self.name < other.name
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, InspectionType):
            return (self.group == other.group and
                    self.name == other.name)
        else:
            return NotImplemented

    def __str__(self):
        return f"InspectionType ({self.group.name}::{self.name})"


class InspectionProblemSeverity(enum.Enum):
    """
    TODO: needs class summary
    """

    TYPO = 'TYPO'
    WEAK = 'WEAK WARNING'
    WARNING = 'WARNING'
    INFO = 'INFO'
    ERROR = 'ERROR'


# class InspectionProblemClass:
#     """
#     TODO: needs class summary
#     """
#
#     def __init__(self,
#                  class_inspection: InspectionType,
#                  class_description: str,
#                  class_severity: InspectionProblemSeverity):
#         """
#         Initialize new instance of the InspectionProblemClass class.
#
#         :param class_inspection: problem class inspection type
#         :param class_description: problem class description
#         :param class_severity: problem class severity
#         """
#         self.inspection = class_inspection
#         self.description = class_description
#         self.severity = class_severity
#
#     def __lt__(self, other):
#         if isinstance(other, InspectionProblemClass):
#             return self.inspection.name < other.inspection.name
#         else:
#             return NotImplemented
#
#     def __eq__(self, other):
#         if isinstance(other, InspectionProblemClass):
#             return (self.severity == other.severity and
#                     self.description == other.description)
#         else:
#             return NotImplemented
#
#     def __str__(self):
#         return f"[{self.severity.value}] [{self.inspection}] {self.description}"


class InspectionProblem:
    """
    TODO: needs class summary
    """

    def __init__(self, inspection_type: InspectionType, problem_severity: InspectionProblemSeverity,
                 problem_description: str, problem_file: str, problem_line: int, problem_details: str):
        """
        Initialize instance of the InspectionProblem class.

        :param inspection_type: inspection type
        :param problem_file: problem file path
        :param problem_line: problem line number
        :param problem_severity: problem severity
        :param problem_description: problem description
        :param problem_details: problem description
        """
        self.type = inspection_type
        self.file = problem_file
        self.line = problem_line
        self.severity = problem_severity
        self.description = problem_description
        self.details = problem_details

    def __eq__(self, other):
        if isinstance(other, InspectionProblem):
            return (self.type == other.type and
                    self.file == other.file and
                    self.line == other.line and
                    self.severity == other.severity and
                    self.description == other.description and
                    self.details == other.details)
        else:
            return NotImplemented

    @property
    def snippet(self):
        pass

    def __str__(self):
        return f"{self.type} {self.details} at {self.file}:{self.line}"


class InspectionResults:
    """
    TODO: needs class summary
    """

    profile: InspectionProfile
    """
    Inspection profile
    """

    problems: typing.Sequence[InspectionProblem]
    """
    Inspection problems
    """

    def __init__(self, project_dir: str, results_dir: str, configuration: lintforbrains.config.Configuration):
        """
        Initialize instance of the InspectionResults class.

        :param results_dir: results directory
        """
        self.project_dir = os.path.normpath(project_dir)
        self.results_dir = os.path.normpath(results_dir)
        self.configuration = configuration

        self._load_results()

    def _load_results(self):
        self.profile = self._load_results_inspection_profile()
        self.problems = self._load_results_inspection_problems()

    def _load_results_inspection_profile(self):
        profile_path = os.path.join(self.results_dir, '.descriptions.xml')
        _LOG.debug("Parsing {}".format(profile_path))
        profile = self._parse_inspection_profile_fromfile(profile_path)
        return profile

    def _find_inspection_type(self, inspection_name: str):
        for group_name in self.profile.groups:
            if inspection_name in self.profile.groups[group_name].inspections:
                return self.profile.groups[group_name].inspections[inspection_name]
        return None

    def _load_results_inspection_problems(self):
        problems = []
        for e in pathlib.Path(self.results_dir).iterdir():
            if e.is_file() and e.suffix == '.xml':
                problems_file = str(e)
                inspection_name = e.stem
                inspection_type = self._find_inspection_type(inspection_name)
                _LOG.debug(f"Parsing {inspection_type} problems from {problems_file}")
                problems.extend(self._parse_inspection_problems_fromfile(inspection_type, problems_file))
        return problems

    def _parse_inspection_profile_xml(self, e: etree.Element):
        """
        Parse an inspection profile XML element
        """

        profile_name = e.get('profile')
        profile = InspectionProfile(profile_name)

        _LOG.debug(f"Parsed {profile}")

        for c in e.iter('group'):
            self._parse_inspection_group_xml(profile, c)

        return profile

    def _parse_inspection_group_xml(self, profile: InspectionProfile, e: etree.Element):
        """
        Parse an inspection group XML element
        """

        group_name = e.get('name')
        group = InspectionGroup(profile, group_name)

        _LOG.debug(f"Parsed {group}")

        for c in e.iter('inspection'):
            self._parse_inspection_rule_xml(group, c)

        return group

    def _parse_inspection_rule_xml(self, group: InspectionGroup, e: etree.Element):
        """
        Parse an inspection rule XML element
        """

        rule_name = e.get('shortName')
        rule_title = e.get('displayName')
        rule_enabled = e.get('enabled')
        rule_desc = e.text

        rule = InspectionType(group, rule_name, rule_title, rule_desc, rule_enabled)

        _LOG.debug(f"Parsed {rule}")

        return rule

    def _parse_inspection_profile_fromfile(self, file: str):
        """
        Parse profile XML from a file
        """
        return self._parse_inspection_profile_xml(etree.parse(file).getroot())

    def _parse_inspection_problems_fromfile(self, inspection_type: InspectionType, file: str):
        """
        Parse problems XML from a file
        """
        return self._parse_inspection_problems_xml(inspection_type, etree.parse(file).getroot())

    def _parse_inspection_problems_xml(self, inspection_type: InspectionType, e: etree.Element):
        """
        Parse problems XML element
        """

        problems = []

        for c in e.iter('problem'):
            problem_class = c.find('problem_class')
            problem_severity = InspectionProblemSeverity(problem_class.get('severity'))
            problem_description = problem_class.text

            problem_file = substitute(c.findtext('file'), {
                'PROJECT_DIR': self.project_dir
            })
            problem_line = int(c.findtext('line'))
            problem_details = c.findtext('description')

            problem = InspectionProblem(inspection_type,
                                        problem_severity,
                                        problem_description,
                                        problem_file,
                                        problem_line,
                                        problem_details)

            problems.append(problem)

        return problems
