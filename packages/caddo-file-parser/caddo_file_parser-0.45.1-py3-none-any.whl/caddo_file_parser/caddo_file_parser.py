import os
import zipfile
import io
import shutil

from yaml import SafeLoader

from caddo_file_parser.models.caddo_file import CaddoFile
import pandas as pd
import yaml

from caddo_file_parser.models.index_set import IndexSet
from caddo_file_parser.models.run import Run
from caddo_file_parser.settings.generation_settings_loader import GenerationSettingsLoader
from caddo_file_parser.validation.caddo_file_validator import CaddoFileValidator


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(Dumper, self).increase_indent(flow, False)


class CaddoFileParser:

    def create_file(self, caddo_file: CaddoFile):
        CaddoFileValidator().validate(caddo_file)
        self.save_data(caddo_file)
        self.save_runs(caddo_file)
        self.save_seeds(caddo_file)
        self.pack_to_caddo_file(caddo_file)
        self.remove_unused_file(caddo_file)

    def save_data(self, caddo_file):
        pd.DataFrame(caddo_file.data).to_csv(
            "data.csv",
            sep=caddo_file.settings.data_output_file_separator,
            index=False
        )

    def save_runs(self, caddo_file):
        for run in caddo_file.runs:
            self.save_index_sets(run)

    def save_seeds(self, caddo_file):
        with open("seeds.yaml", 'w') as file:
            file_content = {
                "seeds": caddo_file.seeds,
            }
            yaml.dump(file_content, file, Dumper=Dumper, default_flow_style=False)

    def save_index_sets(self, run):
        for index_set in run.index_sets:
            index_set_number = index_set.number
            train_indexes = index_set.train_indexes
            test_indexes = index_set.test_indexes
            seed = index_set.seed
            file_content = {
                "number": index_set_number,
                "train_indexes": train_indexes,
                "test_indexes": test_indexes,
                "seed": seed
            }
            with open(f"index_set_{index_set_number}_run_{run.number}.yaml", 'w') as file:
                yaml.dump(file_content, file, Dumper=Dumper, default_flow_style=False)

    def copy_file(self, from_path, new_file_name):
        try:
            shutil.copy2(from_path, new_file_name)
        except:
            print(f"{new_file_name} already exists in current directory")

    def pack_to_caddo_file(self, caddo_file):
        filenames = []
        for run in caddo_file.runs:
            filenames += [f"index_set_{index_set.number}_run_{run.number}.yaml" for index_set in run.index_sets]
        self.copy_file(caddo_file.settings.data_settings_file_path, "settings.yaml")
        self.copy_file(caddo_file.settings.data_splitting_folding_seeds_file_path, "seeds.yaml")

        filenames += ["data.csv"] + ['settings.yaml'] + ["seeds.yaml"]
        with zipfile.ZipFile(f"{caddo_file.settings.data_output_file_name}.caddo", "w") as archive:
            for filename in filenames:
                archive.write(filename)

    def remove_if_file_was_copied_to_working_dir(self, settings_file_path, file_name):
        if settings_file_path != file_name and settings_file_path != f"./{file_name}":
            os.remove(file_name)

    def remove_unused_file(self, caddo_file):
        for run in caddo_file.runs:
            filenames = [f"index_set_{index_set.number}_run_{run.number}.yaml" for index_set in run.index_sets]
            for file in filenames:
                os.remove(file)
        self.remove_if_file_was_copied_to_working_dir(caddo_file.settings.data_splitting_folding_seeds_file_path, "seeds.yaml")
        self.remove_if_file_was_copied_to_working_dir(caddo_file.settings.data_settings_file_path, "settings.yaml")
        self.remove_if_file_was_copied_to_working_dir(caddo_file.settings.data_input_path, "data.csv")

    def read_data(self, file_name) -> CaddoFile:
        with zipfile.ZipFile(file_name + ".caddo", "r") as zf:
            generation_settings = self.read_settings(zf)
            data = self.read_csv_data(zf, generation_settings)
            runs = self.read_runs(zf, generation_settings)
            seeds = self.read_seeds_from_zip(zf, generation_settings)
        caddo_file: CaddoFile = CaddoFile(runs, data, generation_settings, seeds)
        CaddoFileValidator().validate(caddo_file)
        return caddo_file

    def read_settings(self, zf):
        settings_file = zf.read("settings.yaml").decode(encoding="utf-8")
        settings_yaml = yaml.load(settings_file, Loader=SafeLoader)
        return GenerationSettingsLoader().load_settings_object(settings_yaml)

    def read_csv_data(self, zf, generation_settings):
        separator = generation_settings.data_output_file_separator
        data_csv = zf.read("data.csv").decode(encoding="utf-8")
        return pd.read_csv(io.StringIO(data_csv), sep=separator)

    def read_runs(self, zf, generation_settings):
        runs = []
        total_runs_number = generation_settings.data_splitting_runs
        total_index_sets_in_run = self._get_total_index_sets_in_run(generation_settings)
        for run_number in range(total_runs_number):
            index_sets = []
            for fold_number in range(total_index_sets_in_run):
                index_set_file = zf.read(f"index_set_{fold_number}_run_{run_number}.yaml").decode(encoding="utf-8")
                index_set = IndexSet.of(yaml.load(index_set_file, Loader=SafeLoader))
                index_sets.append(index_set)
            runs.append(
                Run(
                    seed=index_sets[0].seed,
                    number=run_number,
                    index_sets=index_sets
                )
            )
        return runs

    def read_seeds_from_zip(self, zf, generation_settings):
        if generation_settings.data_splitting_folding_seeds_from_list:
            return generation_settings.data_splitting_folding_seeds_from_list
        else:
            normalized_data_splitting_folding_seeds_file_path = \
                os.path.basename(generation_settings.data_splitting_folding_seeds_file_path)
            seeds_file = zf.read(f"{normalized_data_splitting_folding_seeds_file_path}").decode(encoding="utf-8")
            return yaml.load(seeds_file, Loader=SafeLoader)["seeds"]

    def read_seeds(self, generation_settings):
        if generation_settings.data_splitting_folding_seeds_file_path != '':
            with open(generation_settings.data_splitting_folding_seeds_file_path) as f:
                return yaml.load(f, Loader=SafeLoader)["seeds"]
        else:
            return generation_settings.data_splitting_folding_seeds_from_list

    def _get_total_index_sets_in_run(self, generation_settings):
        if generation_settings.data_splitting_folding_method is not None:
            return generation_settings.data_splitting_folding_number
        else:
            raise AttributeError("There is no splitting method set")
