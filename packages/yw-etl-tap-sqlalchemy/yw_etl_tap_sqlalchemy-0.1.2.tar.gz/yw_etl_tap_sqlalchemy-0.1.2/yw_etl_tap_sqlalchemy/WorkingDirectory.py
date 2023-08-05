import os
from pathlib import Path

from yw_etl_tap_sqlalchemy.utils import Conf, Env

_pwd = Path(os.getcwd())
_wd_name = ".tap-sqlalchemy"


class WorkingDirectory:

    @staticmethod
    def get_sql_dir(conf: dict) -> Path:
        return WorkingDirectory.get_directory(conf) / 'sql'

    @staticmethod
    def get_directory(conf: dict) -> Path:
        """
        1. Configuration Entry: config["sync.working_directory"] (relative to pwd)
        2. Environment Variable: TAP_SQLALCHEMY_HOME (must be absolute path)
        3. Home directory: $HOME/.tap-sqlalchemy
        """
        ok, p = WorkingDirectory._check_conf(conf)
        if ok:
            return p

        ok, p = WorkingDirectory._check_env()
        if ok:
            return p

        return WorkingDirectory._check_home_dir()

    @staticmethod
    def _check_home_dir() -> Path:
        p = Path(os.path.expanduser("~")) / _wd_name
        if p.is_file():
            raise Exception(f"{p} already exists and is a file")
        p.mkdir(exist_ok=True)
        return p

    @staticmethod
    def _check_env() -> (bool, Path):
        v = os.environ.get(Env.SYNC_WORKING_DIRECTORY, None)
        if v is None:
            return False, None

        v = Path(v)
        if not v.is_absolute():
            raise Exception(f"environment variable {Env.SYNC_WORKING_DIRECTORY}={v} is not a absolute path")

        if v.is_file():
            raise Exception(f"{v} already exists and is a file")

        v.mkdir(parents=True, exist_ok=True)
        return True, v

    @staticmethod
    def _check_conf(conf: dict) -> (bool, Path):
        wd = conf.get(Conf.SYNC_WORKING_DIRECTORY, None)
        if wd is None:
            return False, None

        wd = Path(wd)
        if wd.is_file():
            raise Exception(f"{wd} already exists and is a file")

        if not wd.is_absolute():
            wd = _pwd / wd

        wd.mkdir(parents=True, exist_ok=True)
        return True, wd.resolve()

    @staticmethod
    def _has_sql_dir(wd: Path) -> bool:
        return (wd / 'sql').is_dir()
