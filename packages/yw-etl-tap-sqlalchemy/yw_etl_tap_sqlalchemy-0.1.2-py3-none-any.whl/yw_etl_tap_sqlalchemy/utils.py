import logging.config
from pathlib import Path


class Conf:
    SYNC_WORKING_DIRECTORY = "sync.working_directory"


class Env:
    SYNC_WORKING_DIRECTORY = "TAP_SQLALCHEMY_HOME"


# Logger
def _get_logger():
    logging_conf_file = Path(__file__).parent / 'logging.conf'
    logging.config.fileConfig(logging_conf_file)
    return logging.getLogger()


taplog = _get_logger()

# only for test
_TEST_ROOT = (Path(__file__).parent.parent / 'test').absolute()
_TEST_RESOURCE = _TEST_ROOT / 'resource'
