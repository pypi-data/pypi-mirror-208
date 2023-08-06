import os
try:
    import yaml
except ModuleNotFoundError:
    yaml = None

from LordUtils.json_encoder import JEncoder
from LordPath import save_file, read_file
from LordPath.opener import Opener


def load_yaml(y, default=None):
    if yaml is None:
        raise ModuleNotFoundError(' PyYAML - pip install PyYAML ')

    if os.path.isfile(y):
        y = read_file(y, None)
    if y is None:
        return default

    _yaml = yaml.safe_load(y)
    if isinstance(_yaml, dict):
        return _yaml
    elif isinstance(_yaml, list):
        return _yaml
    else:
        return default


def save_yaml(obj, path):
    if yaml is None:
        raise ModuleNotFoundError(' PyYAML - pip install PyYAML ')

    _y = yaml.dump(obj)
    return save_file(path, _y)


class YamlOpener(Opener):
    compatible_endings = ['yaml', 'yml']

    @staticmethod
    def load(file, default=None) -> dict:
        return load_yaml(file, default=None)

    @staticmethod
    def save(obj, file):
        return save_yaml(obj, file)


