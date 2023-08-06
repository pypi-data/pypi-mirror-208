import pickle
from pathlib import Path
from .. import _path_convert

from LordPath import path_check, mkdir
from .base import Opener

# pyobj
# https://www.techcoil.com/blog/how-to-save-and-load-objects-to-and-from-file-in-python-via-facilities-from-the-pickle-module/
# https://www.journaldev.com/15638/python-pickle-example


def save_obj(obj, file: str | Path):
    file: Path = path_check(file)
    mkdir(file.parent)

    with file.open('wb') as f:
        pickle.dump(obj, f)


def load_obj(file: Path | str):
    file = _path_convert(file)
    with file.open('rb') as f:
        data = pickle.load(f)
        return data


class PickleOpener(Opener):
    compatible_endings = ['pickle']

    @staticmethod
    def load(file, default=None) -> dict:
        return load_obj(file)

    @staticmethod
    def save(obj, file):
        return save_obj(obj, file)
