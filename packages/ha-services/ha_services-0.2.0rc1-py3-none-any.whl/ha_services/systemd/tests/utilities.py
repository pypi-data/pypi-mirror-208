import os
import tempfile
from pathlib import Path
from unittest import mock

from bx_py_utils.environ import OverrideEnviron
from bx_py_utils.test_utils.context_managers import MassContextManager

from ha_services.systemd import defaults
from ha_services.systemd.data_classes import BaseSystemdServiceInfo


class MockedCurrentWorkDir(tempfile.TemporaryDirectory):
    def __init__(self, **kwargs):
        self.old_cwd = Path().cwd()
        super().__init__(**kwargs)

    def __enter__(self):
        temp_dir = super().__enter__()
        os.chdir(temp_dir)
        self.temp_path = Path(temp_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        os.chdir(self.old_cwd)


class MockedSys:
    executable = '/mocked/.venv/bin/python3'


class MockedSystemdServiceInfo(MassContextManager):
    """
    Set all values in ha_services/systemd/defaults.py to static ones,
    independent of current user/environment.

    So that creating a SystemdServiceInfo() instance will result in a well known state.

    Note: The work_dir has still a random suffix!
    """

    def __init__(self, prefix: str, SystemdServiceInfoClass):
        self.mocked_cwd = MockedCurrentWorkDir(prefix=prefix)
        assert issubclass(SystemdServiceInfoClass, BaseSystemdServiceInfo)
        self.SystemdServiceInfoClass = SystemdServiceInfoClass

        self.mocks = (
            self.mocked_cwd,
            OverrideEnviron(SUDO_USER='MockedUserName'),
            mock.patch.object(defaults, 'sys', MockedSys()),
        )

    def __enter__(self) -> BaseSystemdServiceInfo:
        super().__enter__()
        temp_path = self.mocked_cwd.temp_path
        mocked_systemd_base_path = temp_path / 'etc-systemd-system'
        mocked_systemd_base_path.mkdir()
        info = self.SystemdServiceInfoClass(systemd_base_path=mocked_systemd_base_path)
        return info
