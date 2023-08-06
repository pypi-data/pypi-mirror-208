from caddo_file_parser.models.index_set import IndexSet


class Run:
    def __init__(self, index_sets: [IndexSet], seed: int, number: int):
        self.index_sets = index_sets
        self.seed = seed
        self.number = number
