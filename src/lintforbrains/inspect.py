import datetime as dt
import os
import subprocess
import random

import lintforbrains.config
import lintforbrains.logging
import lintforbrains.results

_LOG = lintforbrains.logging.get_logger(__name__)


class InspectorError(Exception):
    pass


class Inspection:
    """
    TODO: needs class summary
    """

    project_dir: str
    results_dir: str
    source_dir: str
    output_dir: str
    logfile_path: str
    profile_path: str

    configuration = lintforbrains.config.Configuration

    def __init__(self, project_dir: str, configuration: lintforbrains.config.Configuration):
        """
        Initialize instance of the Inspection class.

        :param project_dir: project directory
        :param configuration: project configuration
        """
        self.project_dir = os.path.abspath(project_dir)
        self.configuration = configuration

        # results_dir is relative to project_dir
        self.results_dir = os.path.normpath(os.path.join(project_dir, configuration.inspect.results_dir))

        # source_dir is relative to project_dir
        self.source_dir = os.path.normpath(os.path.join(project_dir, configuration.inspect.source_dir))

        self.profile_path = configuration.inspect.profile
        if self.profile_path is None:
            self.profile_path = os.path.join(self.project_dir, ".idea/inspectionProfiles/Project_Default.xml")

        self.output_dir = self._prepare_output_dir()

    def _prepare_output_dir(self):
        random_val = random.randint(0, 255)
        output_time = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        output_dir = os.path.join(self.results_dir, "inspection-{}-{}".format(output_time, random_val))
        os.makedirs(output_dir)
        _LOG.debug("Created inspection output dir: {}".format(output_dir))
        return output_dir

    def run(self, debug_level=1):
        """
        Run the inspection.

        :param debug_level: inspection debug level
        :return: inspection results
        """

        command = [os.path.join(lintforbrains.config.PYCHARM_ROOT, "bin", "inspect.sh"),
                   self.project_dir,
                   self.profile_path,
                   self.output_dir]

        if self.source_dir:
            command.extend(["-d", self.source_dir])

        if debug_level:
            command.extend(["-v{}".format(debug_level)])

        _LOG.debug("Executing command: {}".format(command))

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as ex:
            raise InspectorError("Error running inspect (return code = {})".format(ex.returncode)) from ex

