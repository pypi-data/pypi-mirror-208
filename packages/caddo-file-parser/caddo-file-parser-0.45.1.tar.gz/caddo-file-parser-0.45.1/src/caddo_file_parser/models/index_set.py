class IndexSet:
    def __init__(self, number: int, train_indexes: [int], test_indexes: [int], seed: int):
        self.number = number
        self.train_indexes = train_indexes
        self.test_indexes = test_indexes
        self.seed = seed

    @staticmethod
    def of(index_set_yaml_file):
        number = index_set_yaml_file["number"]
        train_indexes = index_set_yaml_file["train_indexes"]
        test_indexes = index_set_yaml_file["test_indexes"]
        seed = index_set_yaml_file["seed"]
        index_set = IndexSet(number, train_indexes, test_indexes, seed)
        return index_set
