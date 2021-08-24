import enum
import os
import typing
import weakref

from lxml import etree

import lintforbrains.logging

_LOG = lintforbrains.logging.get_logger(__name__)


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
        self.groups = weakref.WeakValueDictionary()


class InspectionGroup:
    """
    TODO: needs class summary
    """
    inspections: typing.MutableMapping[str, 'InspectionType']

    def __init__(self, group_profile: InspectionProfile, group_name: str):
        """
        Initialize instance of the InspectionGroup class.

        :param group_profile: parent inspection profile
        :param group_name: inspection group name
        """
        self.profile = group_profile
        self.name = group_name
        self.inspections = weakref.WeakValueDictionary()

        group_profile.groups[group_name] = self


class InspectionType:
    """
    TODO: needs class summary
    """

    def __init__(self,
                 inspection_group: InspectionGroup,
                 inspection_name: str,
                 inspection_title: str,
                 inspection_description: str,
                 inspection_enabled: bool):
        """
        Initialize instance of the InspectionType class.

        :param inspection_group: parent inspection group
        :param inspection_name: inspection rule name
        :param inspection_title: inspection rule title
        :param inspection_description: inspection rule description (html)
        :param inspection_enabled: inspection rule enabled
        """
        self.group = inspection_group
        self.name = inspection_name
        self.title = inspection_title
        self.description = inspection_description
        self.enabled = inspection_enabled

        inspection_group.inspections[inspection_name] = self


class InspectionProblemSeverity(enum.Enum):
    """
    TODO: needs class summary
    """

    TYPO = 'TYPO'
    WEAK = 'WEAK WARNING'
    WARNING = 'WARNING'
    INFO = 'INFO'
    ERROR = 'ERROR'


class InspectionProblemClass:
    """
    TODO: needs class summary
    """

    def __init__(self, inspection_name: str, problem_description: str, problem_severity: InspectionProblemSeverity):
        """
        Initialize new instance of the InspectionProblemClass class.

        :param inspection_name: problem class inspection
        :param problem_description: problem class description
        :param problem_severity: problem class severity
        """
        self.inspection = inspection_name
        self.description = problem_description
        self.severity = problem_severity

    def __eq__(self, other):
        if isinstance(other, InspectionProblemClass):
            return (self.inspection == other.inspection and
                    self.severity == other.severity and
                    self.description == other.description)
        else:
            return NotImplemented

    def __repr__(self):
        return "[{serv}] {desc}".format(serv=self.severity.value, desc=self.description)


class InspectionProblem:
    """
    TODO: needs class summary
    """

    def __init__(self,
                 problem_class: InspectionProblemClass,
                 problem_details: str,
                 problem_file: str,
                 problem_line: int):
        """
        Initialize instance of the InspectionProblem class.

        :param problem_class: problem classification
        :param problem_details: problem description
        :param problem_file: problem file path
        :param problem_line: problem line number
        """
        self.classification = problem_class
        self.details = problem_details
        self.file = problem_file
        self.line = problem_line

    def __eq__(self, other):
        if isinstance(other, InspectionProblem):
            return (self.file == other.file and
                    self.line == other.line and
                    self.classification == other.classification and
                    self.details == other.details)
        else:
            return NotImplemented

    def __repr__(self):
        return "{klass} {desc} at {file}:{line}".format(klass=self.classification,
                                                        desc=self.details,
                                                        file=self.file,
                                                        line=self.line)


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

    def __init__(self, results_dir: str):
        """
        Initialize instance of the InspectionResults class.

        :param results_dir: results directory
        """
        self.results_dir = results_dir

        self._load_results()

    def _load_results(self):
        self.profile = self._load_results_inspection_profile()
        self.problems = self._load_results_inspection_problems()

    def _load_results_inspection_profile(self):
        profile_path = os.path.join(self.results_dir, '.descriptions.xml')
        _LOG.debug("Parsing {}".format(profile_path))
        profile = self._parse_inspection_profile_fromfile(profile_path)
        return profile

    def _load_results_inspection_problems(self):
        problems = []
        with os.scandir(self.results_dir) as dh:
            for e in dh:
                if e.is_file() and e.name != '.descriptions.xml':
                    _LOG.debug("Parsing {}".format(e.path))
                    inspection = os.path.splitext(os.path.basename(e.path))[0]
                    problems.extend(self._parse_inspection_problems_fromfile(inspection, e.path))
        return problems

    def _parse_inspection_profile_xml(self, e: etree.Element):
        """
        Parse an inspection profile XML element
        """

        profile_name = e.get('profile')
        profile = InspectionProfile(profile_name)

        _LOG.debug("Parsed {}".format(profile))

        for c in e.iter('group'):
            self._parse_inspection_group_xml(profile, c)

        return profile

    def _parse_inspection_group_xml(self, profile: InspectionProfile, e: etree.Element):
        """
        Parse an inspection group XML element
        """

        group_name = e.get('name')
        group = InspectionGroup(profile, group_name)

        _LOG.debug("Parsed {}".format(group))

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

        _LOG.debug("Parsed {}".format(rule))

        return rule

    def _parse_inspection_profile_fromfile(self, file: str):
        """
        Parse profile XML from a file
        """
        return self._parse_inspection_profile_xml(etree.parse(file).getroot())

    def _parse_inspection_problems_fromfile(self, inspection: str, file: str):
        """
        Parse problems XML from a file
        """
        return self._parse_inspection_problems_xml(inspection, etree.parse(file).getroot())

    def _parse_inspection_problems_xml(self, problem_name: str, e: etree.Element):
        """
        Parse problems XML element
        """

        problems = []

        for c in e.iter('problem'):
            problem_type = self._parse_inspection_problem_type_xml(problem_name, c.find('problem_class'))
            problem_info = c.findtext('description')
            problem_file = c.findtext('file')
            problem_line = c.findtext('line')

            problem = InspectionProblem(problem_type, problem_info, problem_file, int(problem_line))

            problems.append(problem)

        return problems

    def _parse_inspection_problem_type_xml(self, problem_name: str, e: etree.Element):
        problem_class_severity = e.get('severity')
        problem_class_description = e.text

        return InspectionProblemClass(problem_name,
                                      problem_class_description,
                                      InspectionProblemSeverity(problem_class_severity))


