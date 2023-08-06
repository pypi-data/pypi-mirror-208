from pathlib import Path
from unittest import TestCase

from tomlkit import TOMLDocument

from ha_services.example import DemoSettings
from ha_services.toml_settings.deserialize import toml2dataclass
from ha_services.toml_settings.serialize import dataclass2toml


class TomlSettingsTestCase(TestCase):
    def test_demo_settings(self):
        document = dataclass2toml(instance=DemoSettings())
        self.assertIsInstance(document, TOMLDocument)
        data = document.unwrap()

        self.assertEqual(data['app']['device_name'], 'ha-services-demo')
        self.assertEqual(data['mqtt']['host'], 'mqtt.eclipseprojects.io')
        self.assertEqual(data['systemd']['service_slug'], 'haservices_demo')
        self.assertEqual(data['systemd']['systemd_base_path'], '/etc/systemd/system')

        instance = DemoSettings()
        instance.systemd.systemd_base_path = Path('/foo/bar')

        toml2dataclass(document=document, instance=instance)

        self.assertEqual(instance.systemd.systemd_base_path, Path('/etc/systemd/system'))
