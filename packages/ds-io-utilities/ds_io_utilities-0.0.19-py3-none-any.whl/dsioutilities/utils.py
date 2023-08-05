from alidaargparser import get_asset_property
from importlib.util import find_spec

def input_or_output(name):

    dir = get_asset_property(name, property="direction")
    
    # TODO remove if else when multidataset supported
    if dir is not None:
        return dir
    else:
        if name == "input_dataset" or name == "input-dataset":
            return "input"
        else: 
            return "output"


def packages_are_installed(packages):
    for package in packages:
        if find_spec(package) is None:
            return False
    return True
