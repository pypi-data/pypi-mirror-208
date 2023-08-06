import pandas as pd

from caddo_file_parser.models.run import Run
from caddo_file_parser.settings.generation_settings import GenerationSettings


class CaddoFile:
    def __init__(self, runs: [Run], data: pd.DataFrame, settings: GenerationSettings, seeds: []):
        self.runs = runs
        self.data = data
        self.settings = settings
        self.seeds = seeds

