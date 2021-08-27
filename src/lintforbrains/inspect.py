import datetime as dt
import os
import subprocess
import random
import typing

import jinja2

from lintforbrains import config
from lintforbrains import logging

_LOG = logging.get_logger(__name__)

_DEFAULT_DEBUG_LEVEL = 2

_PYTHON_SDK_LIBRARY_CMD = 'from __future__ import print_function; import sys; ' \
                          'print("\\n".join([p for p in sys.path if p]))'

_PYTHON_SDK_TEMPLATES = jinja2.Environment(loader=jinja2.PackageLoader('lintforbrains'),
                                           autoescape=jinja2.select_autoescape(['xml']))


def run_inspect(project_dir: str, project_config: config.Configuration, pycharm_version: str, pycharm_edition: str,
                pycharm_home_dir: str, pycharm_config_dir: str, python_bin: str, debug_level: int) -> int:
    """
    Run the inspect command
    """

    # run inspector
    inspector = Inspector(pycharm_version,
                          pycharm_edition,
                          pycharm_home_dir,
                          pycharm_config_dir,
                          python_bin,
                          debug_level)

    inspector.run(project_dir, project_config)

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

    def __init__(self, pycharm_version: str, pycharm_edition: str, pycharm_home_dir: str, pycharm_config_dir: str,
                 python_bin: str, debug_level: int):
        """
        Initialize instance of the Inspection class.

        :param pycharm_version: pycharm version
        :param pycharm_edition: pycharm edition
        :param pycharm_home_dir: pycharm home directory
        :param pycharm_config_dir: pycharm config directory
        :param python_bin: python binary path
        :param debug_level: inspector debug level
        """
        self.pycharm_version = pycharm_version
        self.pycharm_edition = pycharm_edition
        self.pycharm_home_dir = pycharm_home_dir
        self.pycharm_config_dir = pycharm_config_dir
        self.python_bin = python_bin
        self.debug_level = debug_level

    def _configure_inspector(self):

        # get information about the python SDK
        python_sdk = self._query_python_sdk(self.python_bin)
        if python_sdk is None:
            pass

        # configure python SDK libs helpers
        python_helpers = "python-ce" if self.pycharm_edition == "community" else "python"
        python_sdk.sdk_libs.extend([
            f"$APPLICATION_HOME_DIR$/plugins/{python_helpers}/helpers/python-skeletons",
            f"$APPLICATION_HOME_DIR$/plugins/{python_helpers}/helpers/typeshed/stdlib"
        ])

        sdk_output_path = os.path.join(self.pycharm_config_dir, 'options', 'jdk.table.xml')
        if not os.path.exists(os.path.dirname(sdk_output_path)):
            os.makedirs(os.path.dirname(sdk_output_path), exist_ok=True)

        with open(sdk_output_path, 'w', encoding='utf-8') as fh:
            fh.write(_PYTHON_SDK_TEMPLATES.get_template('jdk_table_xml.j2').render(runtimes=[python_sdk]))

        _LOG.debug("Wrote SDK config: {}".format(sdk_output_path))

    def _query_python_sdk(self, python_bin: str) -> InspectorSDKInfo:

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
            raise InspectorError("Error getting Python SDK version (return code = {})".format(ex.returncode)) from ex

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
            raise InspectorError("Error querying Python SDK libraries (return code = {})".format(ex.returncode)) from ex

        python_libs = result.stdout.rstrip().splitlines()

        return InspectorSDKInfo("Python 3.9 (lucid-auth)",
                                "Python SDK",
                                python_version,
                                python_bin,
                                python_libs)

    def _prepare_results_dir(self, output_dir):
        random_val = random.randint(0, 9)
        results_timestamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        results_dir = os.path.join(output_dir, "inspection-{}-{}".format(results_timestamp, random_val))
        os.makedirs(results_dir)
        return results_dir

    def _execute_inspector(self, project_dir: str, project_config: config.Configuration):

        # configure the inspector
        self._configure_inspector()

        # results_dir is relative to project_dir
        inspection_output_dir = os.path.normpath(os.path.join(project_dir, project_config.inspect.output_dir))

        # source_dir is relative to project_dir
        inspection_source_dir = os.path.normpath(os.path.join(project_dir, project_config.inspect.source_dir))

        # generate results dir in output_dir
        inspection_results_dir = self._prepare_results_dir(inspection_output_dir)
        _LOG.debug(f"Writing inspection results to {inspection_results_dir}")

        # write logfile to results dir
        inspection_logfile_path = os.path.join(inspection_results_dir, "inspect.log")
        _LOG.debug(f"Writing inspection logfile to {inspection_logfile_path}")

        inspection_profile_path = project_config.inspect.profile
        if inspection_profile_path is None:
            inspection_profile_path = os.path.join(project_dir, ".idea/inspectionProfiles/Project_Default.xml")

        command = [os.path.join(self.pycharm_home_dir, "bin", "inspect.sh"),
                   project_dir,
                   inspection_profile_path,
                   inspection_results_dir]

        if inspection_source_dir:
            command.extend(["-d", inspection_source_dir])

        if self.debug_level:
            command.extend(["-v{}".format(self.debug_level)])

        _LOG.debug("Executing command: {}".format(command))

        try:
            with open(inspection_logfile_path, "w") as outfile:
                subprocess.run(command,
                               stdout=outfile,
                               stderr=subprocess.STDOUT,
                               check=True)
        except subprocess.CalledProcessError as ex:
            raise InspectorError("Error running inspector (return code = {})".format(ex.returncode)) from ex

        _LOG.info(f"Inspection results written to {inspection_results_dir}")

    def run(self, project_dir: str, project_config: config.Configuration):
        """
        Run the inspector.

        :param project_dir: project directory
        :param project_config: project configuration
        """

        self._execute_inspector(project_dir, project_config)
