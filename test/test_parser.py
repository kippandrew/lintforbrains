from . import TestCase

import pyinspector.parser


class ProfileParserTestCase(TestCase):

    def test_parse_profile(self):
        profile = pyinspector.parser.parse_profile("test-data/results/.descriptions.xml")

        self.assertIsInstance(profile, pyinspector.parser.InspectionProfile)


class ProblemParserTestCase(TestCase):

    def test_parse_problems(self):

        problems = pyinspector.parser.parse_problems("test-data/results/PyPep8Inspection.xml")

        self.assertIsInstance(problems, pyinspector.parser.InspectionProfile)
