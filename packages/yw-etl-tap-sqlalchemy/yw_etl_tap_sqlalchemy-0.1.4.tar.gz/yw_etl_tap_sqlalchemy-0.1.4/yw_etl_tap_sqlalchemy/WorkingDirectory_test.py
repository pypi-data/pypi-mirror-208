import os
from pathlib import Path
from unittest import TestCase

from yw_etl_tap_sqlalchemy.WorkingDirectory import WorkingDirectory
from yw_etl_tap_sqlalchemy.utils import Env, Conf


class TestWorkingDirectory(TestCase):
    def test_should_use_home_as_last_resort(self):
        # unset env
        if os.environ.get(Env.SYNC_WORKING_DIRECTORY, None) is not None:
            del os.environ[Env.SYNC_WORKING_DIRECTORY]
        # empty conf
        conf = {}

        rtn = WorkingDirectory.get_directory(conf)
        exp = Path(os.path.expanduser("~")) / ".tap-sqlalchemy"
        self.assertEqual(exp, rtn)
        exp.rmdir()

    def test_should_use_conf(self):
        os.environ[Env.SYNC_WORKING_DIRECTORY] = "working_dir_2"
        conf = {Conf.SYNC_WORKING_DIRECTORY: "working_dir"}

        rtn = WorkingDirectory.get_directory(conf)
        # conf should take precedence
        exp = Path(os.getcwd()) / "working_dir"
        self.assertEqual(exp, rtn)
        exp.rmdir()

    def test_should_use_env(self):
        os.environ[Env.SYNC_WORKING_DIRECTORY] = f"{os.getcwd()}/working_dir_2"
        conf = {}

        rtn = WorkingDirectory.get_directory(conf)
        exp = Path(os.getcwd()) / "working_dir_2"
        self.assertEqual(exp, rtn)
        exp.rmdir()
