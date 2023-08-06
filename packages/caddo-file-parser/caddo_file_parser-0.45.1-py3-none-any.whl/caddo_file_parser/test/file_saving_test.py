import unittest

import yaml
from pandas import DataFrame
from yaml import SafeLoader

from caddo_file_parser.caddo_file_parser import CaddoFileParser
from caddo_file_parser.models.caddo_file import CaddoFile
from caddo_file_parser.models.index_set import IndexSet
from caddo_file_parser.models.run import Run
from caddo_file_parser.settings.generation_settings import GenerationSettings
from caddo_file_parser.settings.generation_settings_loader import GenerationSettingsLoader


class FileSavingTest(unittest.TestCase):
    def test_save_caddo_file(self):
        caddo_file_parser = CaddoFileParser()
        caddo_file = self._create_caddo_file()
        caddo_file_parser.create_file(caddo_file)

    def _create_caddo_file(self):
        settings_loader = GenerationSettingsLoader()
        with open("settings-data.yaml", 'r') as file:
            settings = settings_loader.load_settings_object(yaml.load(file, Loader=SafeLoader))
            caddo_file = CaddoFile(
                runs=[
                    Run(
                        number=1,
                        index_sets=[
                            IndexSet(1, [1, 2, 0], [2, 0, 1], 10),
                            IndexSet(0, [2, 2, 2], [2, 0, 0], 10)
                        ],
                        seed=10
                    ),
                    Run(
                        number=0,
                        index_sets=[
                            IndexSet(1, [1, 1, 2], [1, 2, 1], 11),
                            IndexSet(0, [0, 1, 2], [1, 0, 0], 11)
                        ],
                        seed=11
                    ),
                ],
                data=DataFrame(
                    data=[[0, 1, 2], [1, 3, 4], [2, 5, 6]],
                    columns=["idx", "x__col_A", "y__col_B"]
                ),
                settings=settings,
                seeds=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            )
            return caddo_file
