import os
import typing

from lxml import etree

import lintforbrains.logging
import lintforbrains.utilities

_LOG = lintforbrains.logging.get_logger(__name__)


class ProjectModule:
    module_dir: str
    module_sdk_type: str
    module_sdk_name: str

    def __init__(self, module_dir: str, module_sdk_type: str, module_sdk_name: str):
        """
        Initialize instance of the ProjectModule class.

        :param module_dir: module directory
        :param module_sdk_type: module SDK type
        :param module_sdk_name: module SDK
        """
        self.module_dir = module_dir
        self.module_sdk_name = module_sdk_name
        self.module_sdk_type = module_sdk_type


class Project:
    """

    """

    project_dir: str
    project_sdk_name: str
    project_sdk_type: str
    project_modules: typing.List[ProjectModule]

    def __init__(self, project_dir: str):
        """
        Initialize instance of the Project class.

        :param project_dir: project dir
        """
        self.project_dir = project_dir

        self._load_project_settings(os.path.join(self.project_dir, '.idea', 'misc.xml'))

        self._load_project_modules(os.path.join(self.project_dir, '.idea', 'modules.xml'))

    def _load_project_settings(self, misc_file_path: str):
        if not os.path.exists(misc_file_path):
            pass

        _LOG.debug("Parsing settings file: {}".format(modules_file_path))

    def _parse_settings_xml(self, e:etree.Element):
        assert e.tag.lower() == "project"

    def _load_project_modules(self, modules_file_path: str):
        if not os.path.exists(modules_file_path):
            raise RuntimeError("Unable to load project: project file not found ({}).".format(modules_file_path))

        _LOG.debug("Parsing project file: {}".format(modules_file_path))

        return self._parse_modules_xml(etree.parse(modules_file_path).getroot())

    def _parse_modules_xml(self, e: etree.Element):
        assert e.tag.lower() == "project"

        for c in e.find('component[@name="ProjectModuleManager"]/modules').iter('module'):
            module_file_path = lintforbrains.utilities.substitute(c.get('filepath'), dict(PROJECT_DIR=self.project_dir))

            self._load_project_module(module_file_path)

    def _load_project_module(self, module_file_path: str):
        if not os.path.exists(module_file_path):
            _LOG.warning("Module file not found: {}.".format(module_file_path))
            return

        _LOG.debug("Parsing module file: {}".format(module_file_path))

        return self._parse_project_module_xml(etree.parse(module_file_path).getroot())

    def _parse_project_module_xml(self, e: etree.Element):
        assert e.tag.lower() == "module"

        module_jdk = e.find('component[@name="NewModuleRootManager"]/orderEntry[@type="jdk"]')

        module_sdk_type = module_jdk.get('jdkType')
        module_sdk_name = module_jdk.get('jdkName')

        self.project_modules.append(ProjectModule(self.project_dir, module_sdk_type, module_sdk_name))
