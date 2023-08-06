import math

from caddo_file_parser.models.caddo_file import CaddoFile


class CaddoFileValidator:
    def validate(self, caddo_file: CaddoFile):
        print("Making validation...")
        self._validate_run_consistency(caddo_file)
        self._validate_index_set_number(caddo_file)
        self._validate_index_set_counts_in_runs(caddo_file)
        self._validate_seed_consistency_in_run(caddo_file)
        self._settings_objects_set(caddo_file)
        self._is_at_least_one_x_column(caddo_file)
        self._is_at_least_one_y_column(caddo_file)
        self._data_contains_index_colum(caddo_file)
        self._each_index_in_index_sets_points_to_valid_data(caddo_file)
        self._does_runs_contains_valid_numbering(caddo_file)
        self._does_index_sets_contains_valid_numbering(caddo_file)

    def _validate_run_consistency(self, caddo_file: CaddoFile):
        print("Checking if number of Runs in settings is this same as in cadd_file")
        runs_number_in_settings = caddo_file.settings.data_splitting_runs
        runs_number_in_caddo_file = len(caddo_file.runs)
        print(f"Declared in settings: {runs_number_in_settings}, found in caddo_file {runs_number_in_caddo_file}")
        is_valid = runs_number_in_caddo_file == runs_number_in_settings
        if not is_valid:
            raise AttributeError(
                f"There is inconsistent number of Runs, settings declared {runs_number_in_settings} but found {runs_number_in_caddo_file}")
        print()

    def _validate_index_set_counts_in_runs(self, caddo_file: CaddoFile):
        print(
            "Checking if all Runs have this same number of index_sets and if each index_contains this same number of indexes")
        last_number_of_index_sets = len(caddo_file.runs[0].index_sets)
        last_number_of_train_elements_in_index_set = len(caddo_file.runs[0].index_sets[0].train_indexes)
        last_number_of_test_elements_in_index_set = len(caddo_file.runs[0].index_sets[0].test_indexes)
        for run in caddo_file.runs:
            print(f"Checking run number {run.number}:")
            print(f"Number of index_sets found: {len(run.index_sets)}")
            if (len(run.index_sets)) != last_number_of_index_sets:
                raise AttributeError(
                    f"There is inconsistent number of elements in run {run} and in first run was {last_number_of_index_sets}")
            for index_set in run.index_sets:
                if len(index_set.train_indexes) != last_number_of_train_elements_in_index_set:
                    if math.fabs(last_number_of_train_elements_in_index_set - len(index_set.train_indexes)) == 1:
                        print("index_sets may differ in the number of elements by 1")
                    else:
                        raise AttributeError(
                            f"There is inconsistent number of elements in index_set train indexes {len(index_set.train_indexes)} and in first index set {last_number_of_train_elements_in_index_set}")
                if len(index_set.test_indexes) != last_number_of_test_elements_in_index_set:
                    if math.fabs(last_number_of_test_elements_in_index_set - len(index_set.test_indexes)) == 1:
                        print("index_sets may differ in the number of elements by 1")
                    else:
                        raise AttributeError(
                            f"There is inconsistent number of elements in index_set test indexes {len(index_set.test_indexes)} and in first index set {last_number_of_test_elements_in_index_set}")
            print("All index sets in this run has this same number of test indexes")
            print("All index sets in this run has this same number of train indexes")
            print()

    def _validate_index_set_number(self, caddo_file):
        print("Checking if each run has declared in settings number of index_sets")
        if caddo_file.settings.data_splitting_folding_method is not None:
            index_set_number_in_settings = caddo_file.settings.data_splitting_folding_number
            min_index_set_number_in_caddo_file = min([len(run.index_sets) for run in caddo_file.runs])
            print(f"Declared number of index_sets in each run is: {index_set_number_in_settings}")
            print(f"Minimal number of index_sets found in run is: {min_index_set_number_in_caddo_file}")
            if min_index_set_number_in_caddo_file != index_set_number_in_settings:
                raise AttributeError(
                    f"There is inconsistent number of index_sets, settings declared {index_set_number_in_settings} but found {min_index_set_number_in_caddo_file} in one of runs")
        print()

    def _validate_seed_consistency_in_run(self, caddo_file: CaddoFile):
        print("Checking if seeds in runs are consistent")
        for run in caddo_file.runs:
            seed_in_run = run.seed
            print(f"Found seed in run number {run.number} is {seed_in_run}")
            for index_set in run.index_sets:
                seed_in_index_set = index_set.seed
                print(f"Found seed in index_set is {seed_in_index_set}")
                if seed_in_run != seed_in_index_set:
                    raise AttributeError(
                        f"Seed in index_set {seed_in_index_set} is different than seed in Run {seed_in_run}")
        print()

    def _settings_objects_set(self, caddo_file: CaddoFile):
        print("Checking if settings object is set")
        if caddo_file.settings is None:
            raise AttributeError(f"Settings property not set")
        print()

    def _is_at_least_one_x_column(self, caddo_file: CaddoFile):
        print("Checking if there is at lest one X column")
        data = caddo_file.data
        x_cols_num = len(data.filter(regex="^[xX]__").columns)
        if x_cols_num == 0:
            raise AttributeError(f"There is no column marked as X (starting with x__)")
        print(f"There is {x_cols_num} X columns")
        print()

    def _is_at_least_one_y_column(self, caddo_file: CaddoFile):
        print("Checking if there is at least one Y column")
        data = caddo_file.data
        y_cols_num = len(data.filter(regex="^[yY]__").columns)
        if y_cols_num == 0:
            raise AttributeError(f"There is no column marked as Y (starting with y__)")
        print(f"There is {y_cols_num} Y columns")
        print()

    def _each_index_in_index_sets_points_to_valid_data(self, caddo_file: CaddoFile):
        print("Checking if each index in index_sets points to valid data in data.csv")
        data = caddo_file.data
        for run in caddo_file.runs:
            for index_set in run.index_sets:
                for index in index_set.test_indexes:
                    try:
                        data.loc[index]
                    except KeyError:
                        raise AttributeError(
                            f"In run {run.number} in test index_set {index_set.number} was index {index} that not match data")
                for index in index_set.train_indexes:
                    try:
                        data.loc[index]
                    except KeyError:
                        raise AttributeError(
                            f"In run {run.number} in train index_set {index_set.number} was index {index} that not match data")
        print("All indexes are OK")
        print()

    def _data_contains_index_colum(self, caddo_file: CaddoFile):
        print("Checking if data.csv contains idx column")
        data = caddo_file.data
        if data["idx"] is None:
            raise AttributeError("Data has no idx column, add idx column")
        print("There is idx column")
        print()

    def _does_runs_contains_valid_numbering(self, caddo_file):
        print("Checking if runs have valid numbering")
        runs = caddo_file.runs
        ids_to_match = list(range(len(runs)))
        for run in runs:
            try:
                ids_to_match.remove(run.number)
            except ValueError:
                raise AttributeError(
                    f"Run number {run.number} is out of range. Those should be in range <0,{len(runs)})")
        if len(ids_to_match) > 0:
            raise AttributeError(f"There was Run ids that was missing {ids_to_match}")
        print("All runs have valid number")
        print()

    def _does_index_sets_contains_valid_numbering(self, caddo_file: CaddoFile):
        for run in caddo_file.runs:
            ids_to_match = list(range(len(run.index_sets)))
            for index_set in run.index_sets:
                try:
                    ids_to_match.remove(index_set.number)
                except ValueError:
                    raise AttributeError(
                        f"Run number {run.number} index_set {index_set.number} is out of range. Those should be in range <0,{len(run.index_sets)})")
            if len(ids_to_match) > 0:
                raise AttributeError(f"There was Run ids that was missing {ids_to_match}")
