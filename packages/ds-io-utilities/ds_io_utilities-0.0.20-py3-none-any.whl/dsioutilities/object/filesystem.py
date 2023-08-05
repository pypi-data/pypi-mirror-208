from ..utils import get_asset_property

def get_path(name):
    return get_asset_property(name)

def get_metadata(name):
    return {"type": "filesystem"}
