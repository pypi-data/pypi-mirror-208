from alidaargparser import get_asset_property

def input_or_output(name):
    return get_asset_property(name, property="direction")

def get_dataset_property(name, prop=None):
    return get_asset_property(asset_name=name, property=prop)    
