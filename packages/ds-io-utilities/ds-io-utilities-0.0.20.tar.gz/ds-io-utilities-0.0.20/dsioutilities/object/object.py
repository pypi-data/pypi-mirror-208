from ..dataset import Dataset
import importlib
import os


class ObjectDataset(Dataset):
    dataset_type = os.path.basename(__file__).split('.py')[0]

    def __init__(self, name, dataset_type=None):
        super().__init__(name, dataset_type)

    def get_path(self):
        storage_type = super().get_storage_type().lower()
        get_path = importlib.import_module("." + storage_type, package="dsioutilities.object").get_path
        return get_path(self.name)

    def get_metadata(self):
        storage_type = super().get_storage_type().lower()
        get_metadata = importlib.import_module("." + storage_type, package="dsioutilities.object").get_metadata
        return get_metadata(self.name)