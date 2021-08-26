import itertools
import pathlib
import typing
import os

from lintforbrains import config
from lintforbrains import logging
from lintforbrains.results import *
from lintforbrains.utilities import abort

_LOG = logging.get_logger(__name__)


def run_report(project_dir: str, config_file: str, results_dir: str = None) -> int:
    """
    Run the report command
    """

    # load configuration
    try:
        if config_file is None:
            config_file = os.path.join(project_dir, config.DEFAULT_CONFIG_FILE)
        configuration = config.load_config(config_file)
    except FileNotFoundError:
        abort(f"Failed to load configuration file: {config_file}")
        return

    # find inspection results
    if results_dir is None:
        results_dir = latest_results_dir(project_dir, configuration)
        if results_dir is None:
            abort("Unable to locate inspection results.")
            return

    # load inspection results
    inspection_results = InspectionResults(project_dir, results_dir, configuration)

    # create inspection report
    inspection_report = InspectionReport(inspection_results,
                                         suppress_problems=configuration.report.suppress_problems)

    # write inspection report
    inspection_report_writer = SimpleReportWriter()
    inspection_report_writer.write(inspection_report)

    return 0


class InspectionReportError(Exception):
    pass


class InspectionReport:
    """
    # TODO: needs class summary
    """

    def __init__(self,
                 inspection_results: InspectionResults,
                 suppress_severity: typing.Iterable[str] = None,
                 suppress_files: typing.Iterable[str] = None,
                 suppress_problems: typing.Iterable[str] = None):
        """
        Initialize instance of the InspectionReport class.
        """
        self.suppress_severity = suppress_severity or []
        self.suppress_files = suppress_files or []
        self.suppress_problems = suppress_problems or []
        self.problems = self._process_problems(inspection_results.problems)

    def _is_suppressed_file(self, p: InspectionProblem):
        file_path = pathlib.PurePath(p.file)
        for suppressed_pattern in self.suppress_files:
            if file_path.match(suppressed_pattern):
                return True
        return False

    def _is_suppressed_severity(self, p: InspectionProblem):
        problem_sev = p.severity.value
        for suppressed_sev in self.suppress_severity:
            if suppressed_sev == problem_sev:
                return True
        return False

    def _is_suppressed_problem(self, p: InspectionProblem):
        problem_group = p.type.group.name
        problem_type = p.type.name
        for s in self.suppress_problems:
            suppressed_group, _, suppressed_type = s.partition('::')
            if suppressed_type == problem_type and suppressed_group == problem_group:
                return True
            if suppressed_type is None and suppressed_group == problem_group:
                return True
            if suppressed_type == '*' and suppressed_group == problem_group:
                return True
        return False

    def _process_problems(self, problems: typing.Iterable[InspectionProblem]):
        results = []

        for p in problems:
            if self._is_suppressed_file(p):
                _LOG.debug(f"{p} suppressed by file")
                continue
            if self._is_suppressed_severity(p):
                _LOG.debug(f"{p} suppressed by severity")
                continue
            if self._is_suppressed_problem(p):
                _LOG.debug(f"{p} suppressed by problem")
                continue
            results.append(p)

        return results

    # noinspection PyMethodMayBeStatic
    def group_problems_by_file(self, problems: typing.Iterable[InspectionProblem]):
        def _by_problem_file(p: InspectionProblem):
            return p.file

        return itertools.groupby(sorted(problems, key=_by_problem_file), key=_by_problem_file)

    # noinspection PyMethodMayBeStatic
    def group_problems_by_severity(self, problems: typing.Iterable[InspectionProblem]):
        def _by_problem_severity(p: InspectionProblem):
            return p.severity.value

        return itertools.groupby(sorted(problems, key=_by_problem_severity), key=_by_problem_severity)

    # noinspection PyMethodMayBeStatic
    def group_problems_by_type(self, problems: typing.Iterable[InspectionProblem]):
        def _by_problem_class(p: InspectionProblem):
            return p.type

        return itertools.groupby(sorted(problems, key=_by_problem_class), key=_by_problem_class)

    # # noinspection PyMethodMayBeStatic
    # def group_problems_by_inspection_type(self, problems: typing.Iterable[InspectionProblem]):
    #     def _by_inspection_type(p: InspectionProblem):
    #         return p.klass.inspection
    #
    #     return itertools.groupby(sorted(problems, key=_by_inspection_type), key=_by_inspection_type)
    #
    # # noinspection PyMethodMayBeStatic
    # def group_problems_by_inspection_group(self, problems: typing.Iterable[InspectionProblem]):
    #     def _by_inspection_group(p: InspectionProblem):
    #         return p.klass.inspection.group
    #
    #     return itertools.groupby(sorted(problems, key=_by_inspection_group), key=_by_inspection_group)


class InspectionReportWriter:

    def _begin_write_file(self, report: InspectionReport, file: str):
        pass

    def _end_write_file(self, report: InspectionReport, file: str):
        pass

    def _write_problem(self, report: InspectionReport, problem: InspectionProblem):
        pass

    def write(self, report: InspectionReport):
        for file, file_problems in report.group_problems_by_file(report.problems):
            self._begin_write_file(report, file)

            for problem in file_problems:
                self._write_problem(report, problem)

            self._end_write_file(report, file)


class SimpleReportWriter(InspectionReportWriter):

    def _begin_write_file(self, report: InspectionReport, file: str):
        print(file)

    def _write_problem(self, report: InspectionReport, problem: InspectionProblem):
        print(f"{problem.line} : [{problem.severity.value}] - {problem.details} ({problem.description})")

    def _end_write_file(self, report: InspectionReport, file: str):
        print('--------------')
