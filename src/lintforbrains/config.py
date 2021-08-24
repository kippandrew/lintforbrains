import os

import hcl
import schematics

import lintforbrains.logging

PYCHARM_ROOT = os.getenv('PYCHARM_ROOT', '/opt/pycharm')

PYBUILD_ROOT = os.getenv('PYBUILD_ROOT', '/usr/local/')

_DEFAULT_INSPECT_RESULTS_DIR = "inspection-results/"

_DEFAULT_INSPECT_SOURCE_DIR = None

_DEFAULT_INSPECT_PROFILE = None

_DEFAULT_INSPECT_OUTPUT = 'plain'

_LOG = lintforbrains.logging.getLogger(__name__)


class Configuration(schematics.models.Model):
    """
    TODO: needs class summary
    """

    class ProjectSection(schematics.models.Model):
        """
        ProjectSection defines configure command configuration
        """

        python = schematics.types.StringType()

        install = schematics.types.StringType()

    class InspectSection(schematics.models.Model):
        """
        InspectSection defines inspect command configuration
        """

        source_dir = schematics.types.StringType(default=_DEFAULT_INSPECT_SOURCE_DIR)

        results_dir = schematics.types.StringType(default=_DEFAULT_INSPECT_RESULTS_DIR)

        profile = schematics.types.StringType(default=_DEFAULT_INSPECT_PROFILE)

        output = schematics.types.StringType(default=_DEFAULT_INSPECT_OUTPUT)

        suppress_levels = schematics.types.ListType(schematics.types.StringType)

        suppress_problems = schematics.types.ListType(schematics.types.StringType)

        include_files = schematics.types.ListType(schematics.types.StringType)

        exclude_files = schematics.types.ListType(schematics.types.StringType)

    class ReportSection(schematics.models.Model):
        """
        ReportSection defines report command configuration
        """

    project: ProjectSection = schematics.types.ModelType(ProjectSection)

    inspect: InspectSection = schematics.types.ModelType(InspectSection)

    report: ReportSection = schematics.types.ModelType(ReportSection)


def load_config(config_file, validate=True):
    if not os.path.isfile(config_file):
        raise FileNotFoundError(config_file)

    _LOG.debug("Reading configuration file: {}".format(config_file))

    with open(config_file) as fh:
        config = Configuration(hcl.load(fh))

    if validate:
        _LOG.debug("Validating configuration file: {}".format(config_file))
        config.validate()

    return config
