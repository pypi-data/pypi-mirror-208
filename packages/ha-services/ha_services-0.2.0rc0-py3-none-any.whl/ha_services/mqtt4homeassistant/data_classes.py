from __future__ import annotations

import dataclasses

from bx_py_utils.anonymize import anonymize


@dataclasses.dataclass
class HaValue:
    name: str
    value: int | float | str
    device_class: str  # e.g.: "voltage" / "current" / "energy" etc.
    state_class: str  # e.g.: "measurement" / "total" / "total_increasing" etc.
    unit: str | None  # e.g.: "V" / "A" / "kWh" etc.


@dataclasses.dataclass
class HaValues:
    device_name: str
    values: list[HaValue, ...]
    prefix: str = 'homeassistant'
    component: str = 'sensor'


@dataclasses.dataclass
class HaMqttPayload:
    configs: list[dict, ...]
    state: dict


@dataclasses.dataclass
class MqttSettings:
    """
    Credentials to MQTT server that should be used.
    """

    host: str = 'mqtt.eclipseprojects.io'  # public test MQTT broker service
    port: int = 1883
    user_name: str = ''
    password: str = ''

    def anonymized(self):
        data = dataclasses.asdict(self)
        if self.password:
            data['password'] = anonymize(self.password)
        return data
