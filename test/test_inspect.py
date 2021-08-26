from unittest import mock

import lintforbrains.config
import lintforbrains.inspect

from . import TestCase


class InspectionTestCase(TestCase):

    @mock.patch('lintforbrains.inspect.subprocess')
    def test_run(self, mock_subprocess):

        mock_config = mock.MagicMock()
        mock_config.inspect.profile = 'fake-profile-dir/fake-profile.xml'
        mock_config.inspect.results_dir = 'fake-results-dir/'
        mock_config.inspect.source_dir = 'src/'

        inspection = lintforbrains.inspect.Inspector("fake-project-dir/", mock_config)
        inspection.run()

        mock_subprocess.run.assert_called_with(['/opt/pycharm/bin/inspect.sh',
                                                'fake-project-dir/',
                                                'fake-profile-dir/fake-profile.xml',
                                                'fake-results-dir/',
                                                '-v1'],
                                               check=True)

    @mock.patch('lintforbrains.inspect.subprocess')
    def test_run_with_inspect_dir(self, mock_subprocess):

        mock_config = mock.MagicMock()
        mock_config.inspect.results_dir = 'fake-results-dir/'
        mock_config.inspect.source_dir = 'src/'

        inspector = lintforbrains.inspect.Inspector("fake-project-dir/", mock_config)
        inspector.run()

        mock_subprocess.run.assert_called_with(['/opt/pycharm/bin/inspect.sh',
                                                'fake-project-dir/',
                                                'fake-project-dir/.idea/inspectionProfiles/Project_Default.xml',
                                                'fake-results-dir/',
                                                '-d',
                                                'fake-project-dir/src',
                                                '-v1'],
                                               check=True)
