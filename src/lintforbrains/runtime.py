import os
import subprocess
import sys
import typing

import jinja2

import lintforbrains.config
import lintforbrains.logging

_LOG = lintforbrains.logging.getLogger(__name__)

_PYTHON_SDK = "Python SDK"

_PYTHON_SDK_LIBRARY_CMD = 'from __future__ import print_function; import sys; print("\\n".join([p for p in sys.path if p]))'

_DEFAULT_PYTHON_SDK_INSTALL_PATH = os.path.expanduser('~/.local/python')

_DEFAULT_PYTHON_SDK_INSTALL_OPTIONS = None

templates = jinja2.Environment(loader=jinja2.PackageLoader('lintforbrains'),
                               autoescape=jinja2.select_autoescape(['xml']))


class PythonRuntimeInfo(typing.NamedTuple):
    python_bin: str
    python_version: str
    python_libraries: typing.List[str]


# class ProjectScopes:
#     """
#
#     """
#     pass
#
#
# class ProjectRuntime:
#     """
#     TODO: needs class summary
#     """
#
#     sdk_version: str
#     sdk_home: str
#     sdk_libs: typing.List[str]
#
#     def __init__(self, sdk_home: str, sdk_version: str, sdk_libs: typing.List[str]):
#         """
#         Initialize instance of the ProjectRuntime class.
#
#         :param sdk_name: ProjectRuntime name
#         :param sdk_type: ProjectRuntime type
#         :param sdk_version: ProjectRuntime version
#         :param sdk_home: ProjectRuntime home path
#         :param sdk_libs: ProjectRuntime libs path
#         """
#         self.sdk_name = sdk_name
#         self.sdk_type = sdk_type
#         self.sdk_version = sdk_version
#         self.sdk_home = sdk_home
#         self.sdk_libs = sdk_libs


#
def _get_idea_config_path():
    if sys.platform.lower() == 'darwin':
        pass
    elif sys.platform.lower() == 'linux':
        return os.path.expanduser('~/')
    # return os.path.expanduser()


def _write_sdk_options(idea_config_path: str, runtime: PythonRuntimeInfo):
    sdk_output_path = os.path.join(idea_config_path, 'options', 'jdk.table.xml')

    if not os.path.exists(os.path.dirname(sdk_output_path)):
        os.makedirs(os.path.dirname((sdk_output_path)))

    with open(sdk_output_path, 'w', encoding='utf-8') as fh:
        fh.write(templates.get_template('jdk_table_xml.j2').render(runtimes=[runtime]))

    _LOG.debug("Wrote SDK output: {}".format(sdk_output_path))


def _inspect_python_sdk(python_bin: str) -> PythonRuntimeInfo:
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
                                stderr=subprocess.PIPE,
                                text=True, check=True)
    except subprocess.CalledProcessError as ex:
        raise RuntimeError("Error inspecting ProjectRuntime (return code = {})".format(ex.returncode)) from ex

    python_version = result.stdout.rstrip()

    # get sdk libraries
    command = [python_bin, '-c', _PYTHON_SDK_LIBRARY_CMD]

    _LOG.debug("Executing command: {}".format(command))

    try:
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True)
    except subprocess.CalledProcessError as ex:
        raise RuntimeError("Error inspecting ProjectRuntime (return code = {})".format(ex.returncode)) from ex

    python_libs = result.stdout.rstrip().splitlines()

    return PythonRuntimeInfo(python_bin, python_version, python_libs)


def _install_python_sdk(python_sdk_version: str,
                        python_sdk_install_path: str,
                        python_sdk_install_opts: typing.Mapping[dict, dict] = None,
                        verbose=False):
    """
    TODO: needs summary

    :param python_sdk_version:
    :param python_sdk_install_path:
    :param python_sdk_install_opts:
    :return:
    """

    _LOG.info("Installing Python {} to {} (Options {})".format(python_sdk_version,
                                                       python_sdk_install_path,
                                                       python_sdk_install_opts))

    command = [os.path.join(lintforbrains.config.PYBUILD_ROOT, 'bin', 'python-build')]

    if verbose:
        command.append('--verbose')

    command.append(python_sdk_version)
    command.append(python_sdk_install_path)

    _LOG.debug("Executing Command: {}".format(command))

    try:
        subprocess.run(command,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       text=True,
                       check=True,
                       env=python_sdk_install_opts)
    except subprocess.CalledProcessError as ex:
        raise RuntimeError("Error inspecting ProjectRuntime (return code = {})".format(ex.returncode)) from ex

    return _inspect_python_sdk(os.path.join(python_sdk_install_path, 'bin', 'python'))


def configure_python_sdk(python_sdk_name: str,
                         python_sdk_version: str,
                         python_sdk_type: str = _PYTHON_SDK,
                         python_sdk_install_path: str = None,
                         python_sdk_install_options: typing.Mapping[str, str] = None):
    """

    :param python_sdk_version:
    :param python_sdk_name:
    :param python_sdk_type:
    :param python_sdk_install_path:
    :param python_sdk_install_options:
    :return:
    """

    if not python_sdk_install_path:
        python_sdk_install_path = os.path.join(_DEFAULT_PYTHON_SDK_INSTALL_PATH, python_sdk_name)

    if not python_sdk_install_options:
        python_sdk_install_options = _DEFAULT_PYTHON_SDK_INSTALL_OPTIONS

    python_sdk_bin, python_sdk_version, python_sdk_libs = _install_python_sdk(python_sdk_version,
                                                                              python_sdk_install_path,
                                                                              python_sdk_install_options)

    print(python_sdk_version, python_sdk_bin, python_sdk_libs)

    # runtime = _inspect_python(python_bin)

    # _write_sdk_options(idea_config_path, runtime)

    # lintforbrains.config.bootstrap(python_bin)
    # print(f"bootstrap {python_dir}")
    # template = jinja2.Template(os.path.join(__file__, "templates", "jdk_table_xml.j2"))

    # def configure_scopes(idea_config_path: str):
    #     pass
