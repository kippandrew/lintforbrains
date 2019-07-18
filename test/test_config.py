from unittest import mock

import lintforbrains.config

from . import TestCase


class ConfigTestCase(TestCase):

    def test_config(self):
        config = lintforbrains.config.load_config('test-data/config/lintconfig_01.hcl')
        #
        # self.assertEqual(config.get('project', 'python'), "3.7.4")
        # self.assertEqual(config.get('project', 'source'), "src/")
        # self.assertEqual(config.getlist('project', 'ignore'), ["some-skipped-files/*", "more-skipped-files/*"])
        #
        # self.assertEqual(config.get('inspect', 'profile'), "some profile")
        # self.assertEqual(config.getlist('inspect', 'levels'), ['ERROR', 'WARNING', 'TYPO'])
        # self.assertEqual(config.getlist('inspect', 'suppress'), ["SomeFakeInspection"])
