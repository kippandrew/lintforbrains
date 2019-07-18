from unittest import mock

import lintforbrains.inspect

from . import TestCase


class InspectorTestCase(TestCase):

    @mock.patch('lintforbrains.inspect.subprocess')
    def test_run(self, mock_subprocess):
        inspector = lintforbrains.inspect.Inspection()
        inspector.run("fake-project-dir/", 'fake-results-dir/')

        mock_subprocess.run.assert_called_with(['/opt/pycharm/bin/inspect.sh',
                                                'fake-project-dir/',
                                                'fake-project-dir/.idea/inspectionProfiles/Project_Default.xml',
                                                'fake-results-dir/',
                                                '-v1'],
                                               check=True)

    @mock.patch('lintforbrains.inspect.subprocess')
    def test_run_with_inspect_dir(self, mock_subprocess):
        inspector = lintforbrains.inspect.Inspection()
        inspector.run("fake-project-dir/", 'fake-results-dir/', inspection_dir='fake-project-dir/src')

        mock_subprocess.run.assert_called_with(['/opt/pycharm/bin/inspect.sh',
                                                'fake-project-dir/',
                                                'fake-project-dir/.idea/inspectionProfiles/Project_Default.xml',
                                                'fake-results-dir/',
                                                '-d',
                                                'fake-project-dir/src',
                                                '-v1'],
                                               check=True)
        pass
