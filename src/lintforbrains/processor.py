import typing

import lintforbrains.results
import lintforbrains.logging

_LOG = lintforbrains.logging.get_logger(__name__)


class InspectionProblemFormatter:
    """
    TODO: needs class summary
    """

    def format(self, problem: lintforbrains.results.InspectionProblem):
        return str(problem)


class PlainInspectionProblemFormatter(InspectionProblemFormatter):
    pass


class PrettyInspectionProblemFormatter(InspectionProblemFormatter):
    pass


class JSONInspectionProblemFormatter(InspectionProblemFormatter):
    pass


class InspectionResultProcessor:

    def __init__(self,
                 output: str,
                 suppress_levels: typing.List[str],
                 suppress_problems: typing.List[str] = None,
                 include_patterns: typing.List[str] = None,
                 exclude_patterns: typing.List[str] = None):
        """
        Initialize instance of the InspectionResultsProcessor class.

        :param suppress_levels:
        :param suppress_problems:
        :param include_patterns:
        :param exclude_patterns:
        """

        self.suppress_levels = suppress_levels
        self.suppress_problems = suppress_problems
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns

    def _is_suppressed(self, problem: lintforbrains.results.InspectionProblem):
        pass

    def process(self, results: lintforbrains.results.InspectionResults):

        for p in inspection_results.problems:
            print(p)

