from os import PathLike
from pathlib import Path


from .base import Opener
from .. import read_file, save_file
from . import yaml, json, pickle, toml


def get_opener(file_ending):
    file_ending = file_ending.replace('.', '')
    for cls in Opener.__subclasses__():
        if cls.check(file_ending):
            return cls
    return None


def open_by_type(path: Path, ending=None, default=None):
    if ending is None:
        ending = path.suffix
    opener_cls = get_opener(ending)
    if opener_cls is None:
        return default
    return opener_cls.load(path)


def save_by_type(obj, path, ending=None, default=None):
    if ending is None:
        ending = path.suffix
    opener_cls = get_opener(ending)
    if opener_cls is None:
        return default
    return opener_cls.save(obj, path)


class TextOpener(Opener):
    compatible_endings = ['txt']

    @staticmethod
    def load(file, default=None):
        return read_file(file, default=None)

    @staticmethod
    def save(text, file):
        return save_file(file, text)



