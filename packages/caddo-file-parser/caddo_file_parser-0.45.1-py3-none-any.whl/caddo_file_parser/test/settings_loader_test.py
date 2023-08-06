import unittest

import yaml
from yaml import SafeLoader

from caddo_file_parser.settings.generation_settings_loader import GenerationSettingsLoader


class SettingsLoaderTest(unittest.TestCase):
    def test_load(self):
        settings_loader = GenerationSettingsLoader()
        with open("settings-data.yaml", 'r') as file:
            settings = settings_loader.load_settings_object(yaml.load(file, Loader=SafeLoader))
            print(settings)
