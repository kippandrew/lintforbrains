from . import TestCase

from pyinspector import parser


class ProfileParserTestCase(TestCase):
    PYTHON_PROFILE='''
    '''
    def test_parse_profile(self):
        profile = parser.parse_profile("test-data/results/.descriptions.xml")

        self.assertIsInstance(profile, parser.InspectionProfile)


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
        problems = parser.parse_problems_fromstring(self.PYTHON_PROBLEMS)

        self.assertListEqual([
            parser.Problem("file://$PROJECT_DIR$/src/example_project/api/handler/__init__.py",
                           24,
                           parser.ProblemCategory("PEP 8 coding style violation", parser.ProblemSeverity.WEAK_WARNING),
                           "PEP 8: module level import not at top of file"),

            parser.Problem("file://$PROJECT_DIR$/src/example_project/providers/__init__.py",
                           306,
                           parser.ProblemCategory("PEP 8 coding style violation", parser.ProblemSeverity.WEAK_WARNING),
                           "PEP 8: module level import not at top of file"),

        ], problems)
