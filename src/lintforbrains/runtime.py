import typing
import os
import subprocess

import jinja2

import lintforbrains.logging

_LOG = lintforbrains.logging.getLogger(__name__)

_PYTHON_SDK = "Python SDK"

_PYTHON_SDK_LIBRARY_CMD = 'from __future__ import print_function; import sys; print("\\n".join([p for p in sys.path if p]))'

templates = jinja2.Environment(loader=jinja2.PackageLoader('lintforbrains'),
                               autoescape=jinja2.select_autoescape(['xml']))


class ProjectScopes:
    """

    """
    pass


class ProjectRuntime:
    """
    TODO: needs class summary
    """

    sdk_name: str
    sdk_type: str
    sdk_version: str
    sdk_home: str
    sdk_libs: typing.List[str]

    def __init__(self, sdk_name: str, sdk_type: str, sdk_version: str, sdk_home: str, sdk_libs: typing.List[str]):
        """
        Initialize instance of the ProjectRuntime class.

        :param sdk_name: ProjectRuntime name
        :param sdk_type: ProjectRuntime type
        :param sdk_version: ProjectRuntime version
        :param sdk_home: ProjectRuntime home path
        :param sdk_libs: ProjectRuntime libs path
        """
        self.sdk_name = sdk_name
        self.sdk_type = sdk_type
        self.sdk_version = sdk_version
        self.sdk_home = sdk_home
        self.sdk_libs = sdk_libs


#
# def _get_config_path(config_dir):
#     if sys.platform.lower() == 'darwin':
#     elif sys.platform.lower() == 'linux':
#         return os.path.expanduser('~/')
#     # return os.path.expanduser()


def _inspect_runtime_python(python_bin: str, sdk_type: str, sdk_name: str):
    # get sdk version
    command = [python_bin, '-V']

    _LOG.debug("Executing command: {}".format(command))

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as ex:
        raise RuntimeError("Error inspecting ProjectRuntime (return code = {})".format(ex.returncode)) from ex

    python_version = result.stdout.rstrip()

    # get sdk libraries
    command = [python_bin, '-c', _PYTHON_SDK_LIBRARY_CMD]

    _LOG.debug("Executing command: {}".format(command))

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as ex:
        raise RuntimeError("Error inspecting ProjectRuntime (return code = {})".format(ex.returncode)) from ex

    python_libs = result.stdout.rstrip().splitlines()

    return ProjectRuntime(sdk_name, sdk_type, python_version, python_bin, python_libs)


def _inspect_runtime(sdk_home: str, sdk_type: str, sdk_name: str):
    """

    :param sdk_name:
    :param sdk_type:
    :param sdk_home:
    :return:
    """

    if sdk_type == _PYTHON_SDK:
        return _inspect_runtime_python(sdk_home, sdk_type, sdk_name)
    else:
        raise RuntimeError("Unsupported ProjectRuntime Type: {}".format(sdk_type))


def _write_sdk_options(idea_config_path: str, runtime: ProjectRuntime):

    sdk_output_path = os.path.join(idea_config_path, 'options', 'jdk.table.xml')

    if not os.path.exists(os.path.dirname(sdk_output_path)):
        os.makedirs(os.path.dirname((sdk_output_path)))

    with open(sdk_output_path, 'w', encoding='utf-8') as fh:
        fh.write(templates.get_template('jdk_table_xml.j2').render(runtimes=[runtime]))

    _LOG.debug("Wrote SDK output: {}".format(sdk_output_path))


def configure_sdk(idea_config_path: str, sdk_home: str, sdk_name, sdk_type: str):
    """

    :param idea_config_path:
    :param sdk_name:
    :param sdk_type:
    :param sdk_home:
    :return:
    """

    runtime = _inspect_runtime(sdk_home, sdk_type, sdk_name)

    _write_sdk_options(idea_config_path, runtime)

    # lintforbrains.config.bootstrap(python_bin)
    # print(f"bootstrap {python_dir}")
    # template = jinja2.Template(os.path.join(__file__, "templates", "jdk_table_xml.j2"))


def configure_scopes(idea_config_path: str):
    pass
