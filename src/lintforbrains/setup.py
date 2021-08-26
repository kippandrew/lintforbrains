import os
import subprocess
import sys
import typing

import jinja2

import lintforbrains.config
import lintforbrains.logging

_LOG = lintforbrains.logging.getLogger(__name__)

_PYTHON_SDK_LIBRARY_CMD = 'from __future__ import print_function; import sys; print("\\n".join([p for p in sys.path if p]))'

templates = jinja2.Environment(loader=jinja2.PackageLoader('lintforbrains'),
                               autoescape=jinja2.select_autoescape(['xml']))


class PythonSDKInfo(typing.NamedTuple):
    sdk_name: str
    sdk_type: str
    sdk_version: str
    sdk_home: str
    sdk_libs: typing.List[str]


def _get_idea_config_path(pycharm_version: str, pycharm_edition: str):
    pycharm_name = "PyCharmCE" if pycharm_edition.lower() == 'community' else "PyCharm"

    if sys.platform.lower() == 'darwin':
        pass
    elif sys.platform.lower() == 'linux':
        return os.path.expanduser(f"~/.config/JetBrains/{pycharm_name}{pycharm_version}")


def _setup_python_sdk(pycharm_version: str, pycharm_edition: str, python_sdk: PythonSDKInfo):
    idea_config_path = _get_idea_config_path(pycharm_version, pycharm_edition)

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
        fh.write(templates.get_template('jdk_table_xml.j2').render(runtimes=[python_sdk]))

    _LOG.debug("Wrote SDK config: {}".format(sdk_output_path))


def _inspect_python_sdk(python_home: str) -> PythonSDKInfo:
    """
    TODO: needs summary

    :param python_home: Python binary path
    :return: python runtime info
    """

    # get sdk version
    command = [python_home, '-V']

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
    command = [python_home, '-c', _PYTHON_SDK_LIBRARY_CMD]

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

    return PythonSDKInfo("Python 3.9 (lucid-auth)",
                         "Python SDK",
                         python_version,
                         python_home,
                         python_libs)


# def _install_python_sdk(python_sdk_version: str,
#                         python_sdk_install_path: str,
#                         python_sdk_install_opts: typing.Mapping[dict, dict] = None,
#                         verbose=False):
#     """
#     TODO: needs summary
#
#     :param python_sdk_version:
#     :param python_sdk_install_path:
#     :param python_sdk_install_opts:
#     :return:
#     """
#
#     _LOG.info("Installing Python {} to {} (Options {})".format(python_sdk_version,
#                                                        python_sdk_install_path,
#                                                        python_sdk_install_opts))
#
#     command = [os.path.join(lintforbrains.config.PYBUILD_ROOT, 'bin', 'python-build')]
#
#     if verbose:
#         command.append('--verbose')
#
#     command.append(python_sdk_version)
#     command.append(python_sdk_install_path)
#
#     _LOG.debug("Executing Command: {}".format(command))
#
#     try:
#         subprocess.run(command,
#                        stdout=subprocess.PIPE,
#                        stderr=subprocess.PIPE,
#                        text=True,
#                        check=True,
#                        env=python_sdk_install_opts)
#     except subprocess.CalledProcessError as ex:
#         raise RuntimeError("Error inspecting ProjectRuntime (return code = {})".format(ex.returncode)) from ex
#
#     return _inspect_python_sdk(os.path.join(python_sdk_install_path, 'bin', 'python'))


def run_setup(pycharm_edition: str, pycharm_version: str, python_bin: str):
    # if not python_sdk_install_path:
    #     python_sdk_install_path = os.path.join(_DEFAULT_PYTHON_SDK_INSTALL_PATH, python_sdk_name)
    #
    # if not python_sdk_install_options:
    #     python_sdk_install_options = _DEFAULT_PYTHON_SDK_INSTALL_OPTIONS
    #
    # python_sdk_bin, python_sdk_version, python_sdk_libs = _install_python_sdk(python_sdk_version,
    #                                                                           python_sdk_install_path,
    #                                                                           python_sdk_install_options)
    #
    # print(python_sdk_version, python_sdk_bin, python_sdk_libs)

    python_sdk = _inspect_python_sdk(python_bin)
    if python_sdk is None:
        pass

    _setup_python_sdk(pycharm_version, pycharm_edition, python_sdk)

    # lintforbrains.config.bootstrap(python_bin)
    # print(f"bootstrap {python_dir}")
    # template = jinja2.Template(os.path.join(__file__, "templates", "jdk_table_xml.j2"))

    # def configure_scopes(idea_config_path: str):
    #     pass
