import contextlib
import os
import shutil
import tempfile
import zipfile

import lintforbrains.project

from . import TestCase


@contextlib.contextmanager
def extract_project(project_zip: str):
    extract_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(project_zip) as zf:
            zf.extractall(extract_dir)

        yield extract_dir

    finally:
        shutil.rmtree(extract_dir)


class ProjectTestCase(TestCase):

    def test_project(self):
        with extract_project('test-data/project/project_01.zip') as extract_dir:
            project = lintforbrains.project.Project(extract_dir)

            self.assertEqual(project.project_dir, extract_dir)

            self.assertEqual(len(project.project_modules), 1)

            self.assertEqual(project.project_modules[0].module_dir, extract_dir)
            self.assertEqual(project.project_modules[0].module_sdk_name, 'Python 3.6.5')
            self.assertEqual(project.project_modules[0].module_sdk_type, 'Python SDK')

        with extract_project('test-data/project/project_02.zip') as extract_dir:
            project = lintforbrains.project.Project(extract_dir)

            self.assertEqual(project.project_dir, extract_dir)

            self.assertEqual(len(project.project_modules), 1)

            self.assertEqual(project.project_modules[0].module_dir, extract_dir)
            self.assertEqual(project.project_modules[0].module_sdk_name, 'Python 3.6.5')
            self.assertEqual(project.project_modules[0].module_sdk_type, 'Python SDK')
