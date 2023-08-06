import os
import json

from LordUtils.json_encoder import JEncoder

from LordPath import save_file, read_file
from .base import Opener


def load_json(j, default=None):
    if os.path.isfile(j):
        j = read_file(j, None)
    _strip = j.strip()
    if not (_strip.endswith(('}', ']')) and _strip.startswith(('{', '['))):
        return default
    if j is None:
        return default

    _json = json.loads(j)
    return _json


def save_json(obj, path, cls=None):
    if cls is None:
        cls = JEncoder
    _j = json.dumps(obj, indent=2, cls=cls)
    return save_file(path, _j)


class JsonOpener(Opener):
    compatible_endings = ['json']

    @staticmethod
    def load(file, default=None) -> dict:
        return load_json(file, default=None)

    @staticmethod
    def save(obj, file):
        return save_json(obj, file)


__all__ = [
    'load_json'
]