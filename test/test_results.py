import lintforbrains.results

from . import TestCase


class ProfileParserTestCase(TestCase):
    PYTHON_PROFILE = '''
    '''

    def test_parse_profile(self):
        profile = lintforbrains.results._parse_inspection_profile_fromfile("test-data/results/.descriptions.xml")

        self.assertIsInstance(profile, lintforbrains.results.InspectionProfile)


class ProblemParserTestCase(TestCase):
    PYTHON_PROBLEMS = '''<problems is_local_tool="true">
<problem>
  <file>file://$PROJECT_DIR$/src/example_project/api/handler/__init__.py</file>
  <line>24</line>
  <entry_point TYPE="file" FQNAME="file://$PROJECT_DIR$/src/example_project/api/handler/__init__.py" />
  <problem_class severity="WEAK WARNING" attribute_key="INFO_ATTRIBUTES">PEP 8 coding style violation</problem_class>
  <description>PEP 8: module level import not at top of file</description>
</problem>
<problem>
  <file>file://$PROJECT_DIR$/src/example_project/providers/__init__.py</file>
  <line>306</line>
  <entry_point TYPE="file" FQNAME="file://$PROJECT_DIR$/src/example_project/providers/__init__.py" />
  <problem_class severity="WEAK WARNING" attribute_key="INFO_ATTRIBUTES">PEP 8 coding style violation</problem_class>
  <description>PEP 8: module level import not at top of file</description>
</problem>
</problems>'''

    def test_parse_problems(self):
        problems = lintforbrains.results._parse_problems_fromstring("PyPep8Inspection", self.PYTHON_PROBLEMS)

        self.assertListEqual([
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

        ], problems)
