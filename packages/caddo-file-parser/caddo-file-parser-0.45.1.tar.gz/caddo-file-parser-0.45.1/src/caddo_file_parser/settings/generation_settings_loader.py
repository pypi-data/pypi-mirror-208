from caddo_file_parser.settings.generation_settings import GenerationSettings
from caddo_file_parser.validation.settings_validator import SettingsValidator


class GenerationSettingsLoader:
    def load_settings_object(self, settings_file):
        settings_data: GenerationSettings = GenerationSettings()
        if settings_file["data"]["settings_file"]["path"] is not None:
            settings_data.data_settings_file_path = settings_file["data"]["settings_file"]["path"]
        else:
            settings_data.data_settings_file_path = "./settings.yaml"
        settings_data.data_input_path = settings_file["data"]["input"]["path"]
        settings_data.data_input_separator = settings_file["data"]["input"]["separator"]
        settings_data.data_extraction_function_path = settings_file["data"]['extraction']['function']['path']
        settings_data.data_splitting_folding_number = settings_file["data"]['splitting']['folding']['number']
        settings_data.data_splitting_runs = settings_file["data"]['splitting']['runs']
        settings_data.data_output_file_name = settings_file["data"]['output']['file']['name']
        settings_data.data_splitting_folding_method = settings_file["data"]['splitting']['folding']['method']
        if settings_file["data"]['splitting']['folding']['seeds']['from_list'] is not None:
            settings_data.data_splitting_folding_seeds_from_list = settings_file["data"]['splitting']['folding']['seeds']['from_list']
        if settings_file["data"]['splitting']['folding']['seeds']['from_file'] is not None:
            settings_data.data_splitting_folding_seeds_file_path = settings_file["data"]['splitting']['folding']['seeds']['from_file']
        settings_data.data_output_file_separator = settings_file["data"]['output']['file']['separator']
        SettingsValidator().validate(settings_data)
        return settings_data
