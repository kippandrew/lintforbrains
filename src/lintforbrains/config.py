import os

import hcl
import schematics

import lintforbrains.logging

_LOG = lintforbrains.logging.getLogger(__name__)

PYCHARM_ROOT = os.getenv('PYCHARM_ROOT', '/opt/pycharm')

PYBUILD_ROOT = os.getenv('PYBUILD_ROOT', '/usr/local/')

_DEFAULT_INSPECT_RESULTS_DIR = "inspection-results/"

_DEFAULT_INSPECT_SOURCE_DIR = None

_DEFAULT_INSPECT_PROFILE = None

_DEFAULT_INSPECT_LEVELS = ['ERROR', 'WARNING', 'WEAK WARNING']


class Configuration(schematics.models.Model):
    """
    TODO: needs class summary
    """

    class InspectSection(schematics.models.Model):
        """
        InspectSection defines inspect command configuration
        """

        source_dir = schematics.types.StringType(default=_DEFAULT_INSPECT_SOURCE_DIR)

        results_dir = schematics.types.StringType(default=_DEFAULT_INSPECT_RESULTS_DIR)

        profile = schematics.types.StringType(default=_DEFAULT_INSPECT_PROFILE)

        levels = schematics.types.ListType(schematics.types.StringType, default=_DEFAULT_INSPECT_LEVELS)

        suppress = schematics.types.ListType(schematics.types.StringType)

        include = schematics.types.ListType(schematics.types.StringType)

        exclude = schematics.types.ListType(schematics.types.StringType)

        output = schematics.types.StringType()

    class ReportSection(schematics.models.Model):
        """
        ReportSection defines report command configuration
        """

    inspect: InspectSection = schematics.types.ModelType(InspectSection)

    report: ReportSection = schematics.types.ModelType(ReportSection)


def load_config(config_file, validate=True):
    if not os.path.isfile(config_file):
        raise FileNotFoundError(config_file)

    _LOG.debug("Reading configuration file: {}".format(config_file))

    with open(config_file) as fh:
        config = Configuration(hcl.load(fh))

    if validate:
        config.validate()

    return config
