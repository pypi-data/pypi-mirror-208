from unittest import TestCase
from unittest.mock import patch

from bx_py_utils.path import assert_is_file
from bx_py_utils.test_utils.redirect import RedirectOut
from manageprojects.test_utils.subprocess import SubprocessCallMock
from manageprojects.utilities import subprocess_utils


from ha_services.cli_tools.test_utils.assertion import assert_in
from ha_services.example import SystemdServiceInfo
from ha_services.systemd.api import ServiceControl
from ha_services.systemd.tests.utilities import MockedSystemdServiceInfo


class MockedShutilWhich:
    def which(self, command, path=None):
        return f'/usr/bin/{command}'


class SystemdApiTestCase(TestCase):
    def test_print_systemd_file(self):
        with MockedSystemdServiceInfo(
            prefix='test_print_systemd_file_', SystemdServiceInfoClass=SystemdServiceInfo
        ) as info, RedirectOut() as buffer:
            ServiceControl(info=info).debug_systemd_config()

        self.assertEqual(buffer.stderr, '')
        assert_in(
            content=buffer.stdout,
            parts=(
                '[Unit]',
                'Description=HaServices Demo',
                'ExecStart=/mocked/.venv/bin/python3 -m ha_services_app publish-loop',
                'SyslogIdentifier=haservices_demo',
            ),
        )

    def test_service_control(self):
        with MockedSystemdServiceInfo(prefix='test_', SystemdServiceInfoClass=SystemdServiceInfo) as info:
            service_control = ServiceControl(info=info)

            for func_name in ('enable', 'restart', 'stop', 'status', 'remove_systemd_service'):
                with self.subTest(func_name):
                    service_control_func = getattr(service_control, func_name)
                    with RedirectOut() as buffer, self.assertRaises(SystemExit):
                        service_control_func()
                    assert_in(
                        content=buffer.stdout,
                        parts=(
                            'Systemd service file not found',
                            'Hint: Setup systemd service first!',
                        ),
                    )

            with SubprocessCallMock() as mock, patch.object(
                subprocess_utils, 'shutil', MockedShutilWhich()
            ), RedirectOut() as buffer:
                service_control.setup_and_restart_systemd_service()

            assert_in(
                content=buffer.stdout,
                parts=(
                    f'Write "{info.service_file_path}"...',
                    'systemctl daemon-reload',
                    'systemctl enable haservices_demo.service',
                    'systemctl restart haservices_demo.service',
                    'systemctl status haservices_demo.service',
                ),
            )
            assert_is_file(info.service_file_path)

            self.assertEqual(
                mock.get_popenargs(),
                [
                    ['/usr/bin/systemctl', 'daemon-reload'],
                    ['/usr/bin/systemctl', 'enable', 'haservices_demo.service'],
                    ['/usr/bin/systemctl', 'restart', 'haservices_demo.service'],
                    ['/usr/bin/systemctl', 'status', 'haservices_demo.service'],
                ],
            )
