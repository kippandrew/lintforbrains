import lintforbrains.config

from . import TestCase


class ConfigTestCase(TestCase):

    def test_config(self):
        config = lintforbrains.config.load_config('test-data/config/lintconfig_01.hcl')

        self.assertEqual(config.project.python, "fake.version.number")
        self.assertEqual(config.project.install, "fake install command")

        self.assertEqual(config.inspect.source_dir, 'fake-source/')
        self.assertEqual(config.inspect.results_dir, 'fake-results/')
        self.assertEqual(config.inspect.suppress_severity, ['TYPO'])
        self.assertEqual(config.inspect.suppress_problems, ['SuppressMe'])
        self.assertEqual(config.inspect.include_files, ['src/include/me/*'])
        self.assertEqual(config.inspect.exclude_files, ['src/exclude/me/*'])
        self.assertEqual(config.inspect.output, 'plain')
