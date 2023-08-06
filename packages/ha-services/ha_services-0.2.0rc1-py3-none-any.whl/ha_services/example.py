import dataclasses
import logging
import os
import resource
import time

from rich import print  # noqa

from ha_services.mqtt4homeassistant.converter import values2mqtt_payload
from ha_services.mqtt4homeassistant.data_classes import HaValue, HaValues, MqttSettings
from ha_services.mqtt4homeassistant.mqtt import HaMqttPublisher
from ha_services.systemd.data_classes import BaseSystemdServiceInfo, BaseSystemdServiceTemplateContext


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SystemdServiceTemplateContext(BaseSystemdServiceTemplateContext):
    """
    HaServices Demo - Context values for the systemd service file content.
    """

    verbose_service_name: str = 'HaServices Demo'


@dataclasses.dataclass
class SystemdServiceInfo(BaseSystemdServiceInfo):
    """
    HaServices Demo - Information for systemd helper functions.
    """

    template_context: SystemdServiceTemplateContext = dataclasses.field(default_factory=SystemdServiceTemplateContext)


@dataclasses.dataclass
class MqttExampleValues:
    """
    Some values used to create DEMO MQTT messages.
    """

    mqtt_payload_prefix: str = 'example'
    device_name: str = 'ha-services-demo'


@dataclasses.dataclass
class DemoSettings:
    """
    This are just settings for the "ha-services" DEMO.
    Will be used in ha_services example commands.
    See "./cli.py --help" for more information.
    """

    # Information how to setup the systemd services:
    systemd: dataclasses = dataclasses.field(default_factory=SystemdServiceInfo)

    # Information about the MQTT server:
    mqtt: dataclasses = dataclasses.field(default_factory=MqttSettings)

    # Example "app" data:
    app: dataclasses = dataclasses.field(default_factory=MqttExampleValues)


def publish_forever(*, user_settings: DemoSettings, verbose):
    """
    Publish "something" to MQTT server. It's just a DEMO ;)
    """
    publisher = HaMqttPublisher(
        settings=user_settings.mqtt,
        verbose=verbose,
        config_count=1,  # Send every time the config
    )

    while True:
        # Just collect something that we can send:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        values = [
            HaValue(
                name='System load 1min.',
                value=os.getloadavg()[0],
                device_class='',
                state_class='measurement',
                unit='',
            ),
            HaValue(
                name='Time in user mode (float seconds)',
                value=usage.ru_utime,
                device_class='',
                state_class='measurement',
                unit='sec',
            ),
            HaValue(
                name='Time in system mode (float seconds)',
                value=usage.ru_stime,
                device_class='',
                state_class='measurement',
                unit='sec',
            ),
        ]

        # Collect information:
        ha_values = HaValues(
            device_name=user_settings.app.device_name,
            values=values,
        )

        # Create Payload:
        ha_mqtt_payload = values2mqtt_payload(values=ha_values, name_prefix=user_settings.app.mqtt_payload_prefix)

        # Send vial MQTT to HomeAssistant:
        publisher.publish2homeassistant(ha_mqtt_payload=ha_mqtt_payload)

        print('Wait', end='...')
        for i in range(10, 1, -1):
            time.sleep(1)
            print(i, end='...')
