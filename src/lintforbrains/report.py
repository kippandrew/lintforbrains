import typing
import itertools

import lintforbrains.logging
import lintforbrains.results

_LOG = lintforbrains.logging.get_logger(__name__)


class InspectionReportError(Exception):
    pass


_ProblemsIterable = typing.Iterable[lintforbrains.results.InspectionProblem]

_ProblemsByInspectionGroup = typing.Iterable[
    typing.Tuple[
        lintforbrains.results.InspectionGroup,
        _ProblemsIterable
    ]
]

_ProblemsByInspectionType = typing.Iterable[
    typing.Tuple[
        lintforbrains.results.InspectionType,
        _ProblemsIterable
    ]
]

_ProblemsByProblemType = typing.Iterable[
    typing.Tuple[
        lintforbrains.results.InspectionProblemClass,
        _ProblemsIterable
    ]
]

_ProblemsByProblemSeverity = typing.Iterable[
    typing.Tuple[
        lintforbrains.results.InspectionProblemSeverity,
        _ProblemsIterable
    ]
]


class InspectionReport:
    """
    # TODO: needs class summary
    """

    def __init__(self,
                 project_dir: str,
                 inspection_profile: lintforbrains.results.InspectionProfile,
                 inspection_problems: typing.Iterable[lintforbrains.results.InspectionProblem]):
        """
        Initialize instance of the InspectionReport class.
        """
        self.project_dir = project_dir

        self.profile = inspection_profile
        self.problems = inspection_problems

        self.inspections = self._gather_inspections()

        self.summary_of_problems_by_inspection_type = None
        self.summary_of_problems_by_inspection_group = None

        self._generate_report()

    def _gather_inspections(self):
        inspections = {}
        for g in self.profile.groups.values():
            for key, value in g.inspections.items():
                inspections[key] = value
        return inspections

    def _problems_by_inspection_group(self, problems: _ProblemsIterable) -> _ProblemsByInspectionGroup:
        def _by_inspection_group(p: lintforbrains.results.InspectionProblem):
            return self.inspections[p.classification.inspection].group.name

        return itertools.groupby(sorted(problems, key=_by_inspection_group), key=_by_inspection_group)

    def _problems_by_inspection_type(self, problems: _ProblemsIterable) -> _ProblemsByInspectionType:
        def _by_inspection_type(p: lintforbrains.results.InspectionProblem):
            return self.inspections[p.classification.inspection].name

        return itertools.groupby(sorted(problems, key=_by_inspection_type), key=_by_inspection_type)

    def _generate_report(self):
        all_problems = self.problems

        for inspection_group, group_problems in self._problems_by_inspection_group(all_problems):
            for inspection_type, problems in self._problems_by_inspection_type(group_problems):
                print(inspection_group, inspection_type)
                print(all_problems)
        # self._summarize_problems_by_inspection()
        # self._summarize_problems_by_inspection_group()

    def write(self, writer: 'InspectionReportWriter'):
        pass


class InspectionReportWriter:

    def handle_group(self,
                     report: InspectionReport,
                     group: lintforbrains.results.InspectionGroup):
        pass

    def handle_problem(self,
                       report: InspectionReport,
                       inspection: lintforbrains.results.InspectionType,
                       problem: lintforbrains.results.InspectionProblem):
        pass

    def flush(self):
        pass


class SimpleReportWriter(InspectionReportWriter):
    pass
