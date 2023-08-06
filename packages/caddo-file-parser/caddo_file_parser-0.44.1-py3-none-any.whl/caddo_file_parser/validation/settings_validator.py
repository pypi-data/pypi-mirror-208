from os.path import exists

from caddo_file_parser.settings.generation_settings import GenerationSettings

class SettingsValidator:
    def validate(self, settings: GenerationSettings):
        self._check_if_defined_settings_file_path_is_correct(settings)
        self._has_seeds_from_file_or_from_list(settings)
        self._is_path_seed_with_yaml_extension(settings)

    def _check_if_defined_settings_file_path_is_correct(self, settings: GenerationSettings):
        print("Checking if path to settings file is correct")
        if settings.data_settings_file_path is None:
            raise AttributeError(f"Path to settings file is not defined")
        if not exists(settings.data_settings_file_path):
            raise AttributeError(f"Settings file doesn't exists in given location: {settings.data_settings_file_path}")

    def _has_seeds_from_file_or_from_list(self, settings: GenerationSettings):
        print("Checking if there is only one seeds option chosen - from list or from file")
        if len(settings.data_splitting_folding_seeds_from_list) > 0 and \
                settings.data_splitting_folding_seeds_file_path != '':
            raise AttributeError(
                f"The seeds can be read from file OR from list - There should be only one option chosen")

    def _is_path_seed_with_yaml_extension(self, settings: GenerationSettings):
        if settings.data_splitting_folding_seeds_file_path != '':
            print("Checking if a seed file has yaml extension")
            if settings.data_splitting_folding_seeds_file_path != '':
                path = settings.data_splitting_folding_seeds_file_path
                if len(path) < 5:
                    raise AttributeError(
                        f"The seed file must be .yaml")
                if path[len(path) - 5:] != ".yaml":
                    raise AttributeError(
                        f"TThe seed file must be .yaml")
        print()
