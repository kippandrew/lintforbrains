import enum
import typing
import weakref

# noinspection PyPep8Naming
from xml.etree import ElementTree as et

import pyinspector.logging

_LOG = pyinspector.logging.get_logger(__name__)


class InspectionProfile:
    groups: typing.MutableMapping[str, 'InspectionGroup']
    rules: typing.MutableMapping[str, 'InspectionRule']

    def __init__(self, name: str):
        """
        Initialize instance of the InspectionProfile class.

        :param name: inspection profile name
        """
        self.name = name
        self.groups = dict()
        self.rules = dict()


class InspectionGroup:
    rules: typing.MutableMapping[str, 'InspectionRule']

    def __init__(self, profile: InspectionProfile, name: str):
        """
        Initialize instance of the InspectionGroup class.

        :param profile: parent inspection profile
        :param name: inspection group name
        """

        self.profile = weakref.ref(profile)

        self.name = name
        self.rules = weakref.WeakValueDictionary()

        profile.groups[name] = self


class InspectionRule:

    def __init__(self,
                 profile: InspectionProfile,
                 group: InspectionGroup,
                 name: str,
                 title: str,
                 description: str):
        """
        Initialize instance of the InspectionRule class.

        :param profile: parent inspection profile
        :param group: parent inspection group
        :param name: inspection rule name
        :param title: inspection rule title
        :param description: inspection rule description (html)
        """
        self.profile = weakref.ref(profile)
        self.group = weakref.ref(group)
        self.name = name
        self.title = title
        self.description = description

        profile.rules[name] = self
        group.rules[name] = self


class ProblemSeverity(enum.Enum):
    TYPO = 'TYPO'
    WARNING = 'WARNING'
    WEAK_WARNING = 'WEAK WARNING'


class ProblemCategory:

    def __init__(self, description: str, severity: ProblemSeverity):
        """
        Initialize new instance of the ProblemCategory class.

        :param severity:
        :param description:
        """
        self.severity = severity
        self.description = description

    def __eq__(self, other):
        if isinstance(other, ProblemCategory):
            return self.severity == other.severity and self.description == other.description
        else:
            return NotImplemented

    def __repr__(self):
        return "[{sev}] {desc}".format(sev=self.severity.value, desc=self.description)


class Problem:

    def __init__(self, file: str, line: int, category: ProblemCategory, description: str):
        """
        Initialize instance of the Problem class.

        :param file: problem file
        :param line:  problem line
        :param category: problem category
        :param description: problem description
        """
        self.file = file
        self.line = line
        self.category = category
        self.description = description

    def __eq__(self, other):
        if isinstance(other, Problem):
            return (self.file == other.file and
                    self.line == other.line and
                    self.category == other.category and
                    self.description == other.description)
        else:
            return NotImplemented

    def __repr__(self):
        return "{category} ({desc}) at {file}:{line}".format(desc=self.description,
                                                             category=self.category,
                                                             file=self.file,
                                                             line=self.line)


class ParseError(Exception):
    pass


def _parse_inspection_profile_xml(e: et.Element):
    """
    Parse an inspection profile XML element
    """

    profile_name = e.get('profile')
    profile = InspectionProfile(profile_name)

    _LOG.debug("Parsed {}".format(profile))

    for c in e.iter('group'):
        _parse_inspection_group_xml(profile, c)

    return profile


def _parse_inspection_group_xml(profile: InspectionProfile, e: et.Element):
    """
    Parse an inspection group XML element
    """

    group_name = e.get('name')
    group = InspectionGroup(profile, group_name)

    _LOG.debug("Parsed {}".format(group))

    for c in e.iter('inspection'):
        _parse_inspection_rule_xml(profile, group, c)

    return group


def _parse_inspection_rule_xml(profile: InspectionProfile, group: InspectionGroup, e: et.Element):
    """
    Parse an inspection rule XML element
    """

    rule_name = e.get('shortName')
    rule_title = e.get('displayName')
    rule_desc = e.text

    rule = InspectionRule(profile, group, rule_name, rule_title, rule_desc)

    _LOG.debug("Parsed {}".format(rule))

    return rule


def parse_profile(file: str) -> InspectionProfile:
    """
    Parse profile XML from a file

    :param file: file name or file object
    :return: inspection profile
    """
    return _parse_inspection_profile_xml(et.parse(file).getroot())


def parse_profile_fromstring(source: str) -> InspectionProfile:
    """
    Parse profile XML from a string

    :param source: XML string
    :return: inspection profile
    """
    return _parse_inspection_profile_xml(et.fromstring(source))


def _parse_problem_category(e: et.Element):
    problem_class_severity = e.get('severity')
    problem_class_description = e.text

    return ProblemCategory(problem_class_description, ProblemSeverity(problem_class_severity))


def _parse_problems_xml(e: et.Element):
    """
    Parse problems XML element
    """

    problems = []

    for c in e.iter('problem'):
        problem_file = c.findtext('file')
        problem_line = int(c.findtext('line'))
        problem_desc = c.findtext('description')
        problem_class = _parse_problem_category(c.find('problem_class'))

        problem = Problem(problem_file,
                          problem_line,
                          problem_class,
                          problem_desc)

        problems.append(problem)

    return problems


def parse_problems(file: str) -> typing.List[Problem]:
    """
    Parse problems XML from a file

    :param file: file name or file handle
    :return: list of inspection problems
    """

    return _parse_problems_xml(et.parse(file).getroot())


def parse_problems_fromstring(source: str) -> typing.List[Problem]:
    """
    Parse problems XML from a string

    :param source: XML string
    :return: list of inspection problems
    """

    return _parse_problems_xml(et.fromstring(source))
