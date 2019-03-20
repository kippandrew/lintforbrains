from . import TestCase

import lintforbrains.report
import lintforbrains.results


class InspectionReportTestCase(TestCase):
    FAKE_PROFILE = lintforbrains.results.InspectionProfile("fake")
    FAKE_GROUPS = {
        'Python': lintforbrains.results.InspectionGroup(FAKE_PROFILE, "Python")
    }

    FAKE_INSPECTIONS = [
        lintforbrains.results.InspectionType(FAKE_GROUPS['Python'],
                                         'PyPep8Inspection',
                                         'PEP 8 coding style violation', ("&lt;html&gt;\n"
                                                                          "&lt;body&gt;\n"
                                                                          "This inspection runs the pep8.py tool to "
                                                                          "check for violations of the PEP 8 coding "
                                                                          "style guide.\n"
                                                                          "&lt;/body&gt;\n"
                                                                          "&lt;/html&gt;"),
                                             True),
    ]

    def test_report(self):
        problems = [
            lintforbrains.results.InspectionProblem(
                    lintforbrains.results.InspectionProblemClass(
                            "PyPep8Inspection",
                            "PEP 8 coding style violation",
                            lintforbrains.results.InspectionProblemSeverity.WEAK_WARNING),
                    "PEP 8: module level import not at top of file",
                    "file://$PROJECT_DIR$/src/example_project/api/handler/__init__.py",
                    24),

            lintforbrains.results.InspectionProblem(
                    lintforbrains.results.InspectionProblemClass(
                            "PyPep8Inspection",
                            "PEP 8 coding style violation",
                            lintforbrains.results.InspectionProblemSeverity.WEAK_WARNING
                    ),
                    "PEP 8: module level import not at top of file",
                    "file://$PROJECT_DIR$/src/example_project/providers/__init__.py",
                    306),
        ]

        report = lintforbrains.report.InspectionReport("fake/project/dir", self.FAKE_PROFILE, problems)

        self.assertEqual(report, None)