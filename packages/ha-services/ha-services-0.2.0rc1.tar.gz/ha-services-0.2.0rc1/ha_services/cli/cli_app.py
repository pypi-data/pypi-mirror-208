"""
    CLI for usage
"""
import logging
import sys
from pathlib import Path

import rich_click
import rich_click as click
from bx_py_utils.path import assert_is_file
from rich import print  # noqa
from rich.console import Console
from rich.traceback import install as rich_traceback_install
from rich_click import RichGroup

import ha_services
from ha_services import __version__, constants
from ha_services.example import DemoSettings, SystemdServiceInfo, publish_forever
from ha_services.log_setup import basic_log_setup
from ha_services.mqtt4homeassistant.data_classes import MqttSettings
from ha_services.mqtt4homeassistant.mqtt import get_connected_client
from ha_services.systemd.api import ServiceControl
from ha_services.toml_settings.api import TomlSettings


logger = logging.getLogger(__name__)


PACKAGE_ROOT = Path(ha_services.__file__).parent.parent
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')

OPTION_ARGS_DEFAULT_TRUE = dict(is_flag=True, show_default=True, default=True)
OPTION_ARGS_DEFAULT_FALSE = dict(is_flag=True, show_default=True, default=False)
ARGUMENT_EXISTING_DIR = dict(
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path)
)
ARGUMENT_NOT_EXISTING_DIR = dict(
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        readable=False,
        writable=True,
        path_type=Path,
    )
)
ARGUMENT_EXISTING_FILE = dict(
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path)
)


class ClickGroup(RichGroup):  # FIXME: How to set the "info_name" easier?
    def make_context(self, info_name, *args, **kwargs):
        info_name = './cli.py'
        return super().make_context(info_name, *args, **kwargs)


@click.group(
    cls=ClickGroup,
    epilog=constants.CLI_EPILOG,
)
def cli():
    pass


@click.command()
def version():
    """Print version and exit"""
    # Pseudo command, because the version always printed on every CLI call ;)
    sys.exit(0)


cli.add_command(version)


######################################################################################################

SETTINGS_DIR_NAME = 'ha-services'
SETTINGS_FILE_NAME = 'ha-services-demo'


@click.command()
@click.option('--debug/--no-debug', **OPTION_ARGS_DEFAULT_TRUE)
def edit_settings(debug):
    """
    Edit the settings file. On first call: Create the default one.
    """
    basic_log_setup(debug=debug)
    TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    ).open_in_editor()


cli.add_command(edit_settings)


@click.command()
@click.option('--debug/--no-debug', **OPTION_ARGS_DEFAULT_TRUE)
def print_settings(debug):
    """
    Display (anonymized) MQTT server username and password
    """
    basic_log_setup(debug=debug)
    TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    ).print_settings()


cli.add_command(print_settings)


######################################################################################################
# Manage systemd service commands:


@click.command()
@click.option('--debug/--no-debug', **OPTION_ARGS_DEFAULT_TRUE)
def debug_systemd_config(debug):
    """
    Print Systemd service template + context + rendered file content.
    """
    basic_log_setup(debug=debug)
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    )
    user_settings: DemoSettings = toml_settings.get_user_settings(debug=True)
    systemd_settings: SystemdServiceInfo = user_settings.systemd

    ServiceControl(info=systemd_settings).debug_systemd_config()


cli.add_command(debug_systemd_config)


@click.command()
@click.option('--debug/--no-debug', **OPTION_ARGS_DEFAULT_TRUE)
def setup_systemd_service(debug):
    """
    Write Systemd service file, enable it and (re-)start the service. (May need sudo)
    """
    basic_log_setup(debug=debug)
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    )
    user_settings: DemoSettings = toml_settings.get_user_settings(debug=True)
    systemd_settings: SystemdServiceInfo = user_settings.systemd

    ServiceControl(info=systemd_settings).setup_and_restart_systemd_service()


cli.add_command(setup_systemd_service)


@click.command()
@click.option('--debug/--no-debug', **OPTION_ARGS_DEFAULT_TRUE)
def remove_systemd_service(debug):
    """
    Write Systemd service file, enable it and (re-)start the service. (May need sudo)
    """
    basic_log_setup(debug=debug)
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    )
    user_settings: DemoSettings = toml_settings.get_user_settings(debug=True)
    systemd_settings: SystemdServiceInfo = user_settings.systemd

    ServiceControl(info=systemd_settings).remove_systemd_service()


cli.add_command(remove_systemd_service)


@click.command()
@click.option('--debug/--no-debug', **OPTION_ARGS_DEFAULT_TRUE)
def systemd_status(debug):
    """
    Display status of systemd service. (May need sudo)
    """
    basic_log_setup(debug=debug)
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    )
    user_settings: DemoSettings = toml_settings.get_user_settings(debug=True)
    systemd_settings: SystemdServiceInfo = user_settings.systemd

    ServiceControl(info=systemd_settings).status()


cli.add_command(systemd_status)


@click.command()
@click.option('--debug/--no-debug', **OPTION_ARGS_DEFAULT_TRUE)
def systemd_stop(debug):
    """
    Stops the systemd service. (May need sudo)
    """
    basic_log_setup(debug=debug)
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    )
    user_settings: DemoSettings = toml_settings.get_user_settings(debug=True)
    systemd_settings: SystemdServiceInfo = user_settings.systemd

    ServiceControl(info=systemd_settings).stop()


cli.add_command(systemd_stop)

######################################################################################################
# MQTT DEMO commands:


@click.command()
@click.option('--debug/--no-debug', **OPTION_ARGS_DEFAULT_FALSE)
def test_mqtt_connection(debug):
    """
    Test connection to MQTT Server
    """
    basic_log_setup(debug=debug)
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    )
    user_settings: DemoSettings = toml_settings.get_user_settings(debug=True)

    settings: MqttSettings = user_settings.mqtt
    mqttc = get_connected_client(settings=settings, verbose=True)
    mqttc.loop_start()
    mqttc.loop_stop()
    mqttc.disconnect()
    print('\n[green]Test succeed[/green], bye ;)')


cli.add_command(test_mqtt_connection)


@click.command()
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('--debug/--no-debug', **OPTION_ARGS_DEFAULT_FALSE)
def publish_loop(verbose, debug):
    """
    Publish data via MQTT for Home Assistant (endless loop)
    """
    basic_log_setup(debug=debug)
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    )
    user_settings: DemoSettings = toml_settings.get_user_settings(debug=True)

    try:
        publish_forever(user_settings=user_settings, verbose=verbose)
    except KeyboardInterrupt:
        print('Bye, bye')


cli.add_command(publish_loop)


######################################################################################################


def main():
    print(f'[bold][green]ha-services[/green] DEMO cli v[cyan]{__version__}')

    console = Console()
    rich_traceback_install(
        width=console.size.width,  # full terminal width
        show_locals=True,
        suppress=[click, rich_click],
        max_frames=2,
    )

    # Execute Click CLI:
    cli.name = './cli.py'
    cli()
