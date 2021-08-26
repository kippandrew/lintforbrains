import datetime as dt
import os
import subprocess
import random
import typing

import jinja2

from lintforbrains import config
from lintforbrains import logging

from lintforbrains.utilities import abort, jetbrains_config_path

_LOG = logging.get_logger(__name__)

_PYTHON_SDK_LIBRARY_CMD = 'from __future__ import print_function; import sys; print("\\n".join([p for p in sys.path if p]))'

_PYTHON_SDK_TEMPLATES = jinja2.Environment(loader=jinja2.PackageLoader('lintforbrains'),
                                           autoescape=jinja2.select_autoescape(['xml']))


def run_inspect(project_dir: str, config_file: str, python_bin: str, pycharm_edition: str, pycharm_version: str) -> int:
    """
    Run the inspect command
    """

    # load configuration
    try:
        if config_file is None:
            config_file = os.path.join(project_dir, config.DEFAULT_CONFIG_FILE)
        inspection_configuration = config.load_config(config_file)
    except FileNotFoundError:
        return abort(f"Failed to load configuration file: {config_file}")

    # run inspector
    inspector = Inspector(project_dir, inspection_configuration)
    inspector.run(python_bin, pycharm_version, pycharm_edition, debug_level=2)

    return 0


class InspectorSDKInfo(typing.NamedTuple):
    sdk_name: str
    sdk_type: str
    sdk_version: str
    sdk_home: str
    sdk_libs: typing.List[str]


class InspectorError(Exception):
    pass


class Inspector:
    """
    TODO: needs class summary
    """

    project_dir: str
    results_dir: str
    source_dir: str
    output_dir: str
    logfile_path: str
    profile_path: str

    configuration = config.Configuration

    def __init__(self, project_dir: str, configuration: config.Configuration):
        """
        Initialize instance of the Inspection class.

        :param project_dir: project directory
        :param configuration: project configuration
        """
        self.project_dir = os.path.normpath(project_dir)
        self.configuration = configuration

        # results_dir is relative to project_dir
        self.results_dir = os.path.normpath(os.path.join(project_dir, configuration.inspect.results_dir))

        # source_dir is relative to project_dir
        self.source_dir = os.path.normpath(os.path.join(project_dir, configuration.inspect.source_dir))

        self.profile_path = configuration.inspect.profile
        if self.profile_path is None:
            self.profile_path = os.path.join(self.project_dir, ".idea/inspectionProfiles/Project_Default.xml")

        self.output_dir = self._prepare_output_dir()

    def _configure_inspector(self, python_bin: str, pycharm_version: str, pycharm_edition: str):

        # get information about the python SDK
        python_sdk = self._inspect_python_sdk(python_bin)
        if python_sdk is None:
            pass

        self._write_python_sdk(pycharm_version, pycharm_edition, python_sdk)

    def _write_python_sdk(self, pycharm_version: str, pycharm_edition: str, python_sdk: InspectorSDKInfo):

        idea_config_path = jetbrains_config_path(pycharm_version, pycharm_edition)

        # configure libs helpers
        python_helpers = "python-ce" if pycharm_edition == 'community' else 'python'
        python_sdk.sdk_libs.extend([
            f"$APPLICATION_HOME_DIR$/plugins/{python_helpers}/helpers/python-skeletons",
            f"$APPLICATION_HOME_DIR$/plugins/{python_helpers}/helpers/typeshed/stdlib"
        ])

        sdk_output_path = os.path.join(idea_config_path, 'options', 'jdk.table.xml')
        if not os.path.exists(os.path.dirname(sdk_output_path)):
            os.makedirs(os.path.dirname(sdk_output_path), exist_ok=True)

        with open(sdk_output_path, 'w', encoding='utf-8') as fh:
            fh.write(_PYTHON_SDK_TEMPLATES.get_template('jdk_table_xml.j2').render(runtimes=[python_sdk]))

        _LOG.debug("Wrote SDK config: {}".format(sdk_output_path))

    def _inspect_python_sdk(self, python_bin: str) -> InspectorSDKInfo:
        """
        TODO: needs summary

        :param python_bin: Python binary path
        :return: python runtime info
        """

        # get sdk version
        command = [python_bin, '-V']

        _LOG.debug("Executing command: {}".format(command))

        try:
            result = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    encoding='utf-8',
                                    universal_newlines=True,
                                    check=True)
        except subprocess.CalledProcessError as ex:
            raise RuntimeError("Error inspecting ProjectRuntime (return code = {})".format(ex.returncode)) from ex

        python_version = result.stdout.rstrip()

        # get sdk libraries
        command = [python_bin, '-c', _PYTHON_SDK_LIBRARY_CMD]

        _LOG.debug("Executing command: {}".format(command))

        try:
            result = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    encoding='utf-8',
                                    universal_newlines=True,
                                    check=True)
        except subprocess.CalledProcessError as ex:
            raise RuntimeError("Error inspecting ProjectRuntime (return code = {})".format(ex.returncode)) from ex

        python_libs = result.stdout.rstrip().splitlines()

        return InspectorSDKInfo("Python 3.9 (lucid-auth)",
                                "Python SDK",
                                python_version,
                                python_bin,
                                python_libs)

    def _prepare_output_dir(self):
        random_val = random.randint(0, 255)
        output_time = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        output_dir = os.path.join(self.results_dir, "inspection-{}-{}".format(output_time, random_val))
        os.makedirs(output_dir)
        _LOG.debug("Created inspection output dir: {}".format(output_dir))
        return output_dir

    def _execute_inspector(self, debug_level: int):

        command = [os.path.join(os.getenv('PYCHARM_ROOT', config.PYCHARM_ROOT), "bin", "inspect.sh"),
                   self.project_dir,
                   self.profile_path,
                   self.output_dir]

        if self.source_dir:
            command.extend(["-d", self.source_dir])

        if debug_level:
            command.extend(["-v{}".format(debug_level)])

        _LOG.debug("Executing command: {}".format(command))

        command_logfile_path = os.path.join(self.output_dir, "inspect.log")

        try:
            _LOG.debug(f"Writing inspector output to {command_logfile_path}")
            with open(command_logfile_path, "w") as outfile:
                subprocess.run(command,
                               stdout=outfile,
                               stderr=subprocess.STDOUT,
                               check=True)
        except subprocess.CalledProcessError as ex:
            raise InspectorError("Error running inspect (return code = {})".format(ex.returncode)) from ex

        _LOG.info(f"Inspection results written to {self.results_dir}")

    def run(self, python_bin, pycharm_version, pycharm_edition, debug_level=1):
        """
        Run the inspection.

        :param debug_level: inspection debug level
        :return: inspection results
        """

        self._configure_inspector(python_bin,
                                  pycharm_version,
                                  pycharm_edition)

        self._execute_inspector(debug_level)
