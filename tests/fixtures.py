from scalecodec.base import RuntimeConfiguration
from scalecodec.type_registry import load_type_registry_preset

RuntimeConfiguration().update_type_registry(load_type_registry_preset("default"))
RuntimeConfiguration().update_type_registry(load_type_registry_preset("kusama"))

genesis_hash = "0xb0a8d493285c2df73290dfb7e61f870f17b41801197a149ca93654499ea3dafe"
spec_version = 2026
