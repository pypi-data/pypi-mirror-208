try:
    import toml
except ModuleNotFoundError:
    toml = None
from .base import Opener


class TomlOpener(Opener):
    compatible_endings = ['toml']

    @staticmethod
    def load(file, default=None) -> dict:
        if toml is None:
            raise ModuleNotFoundError(' TOML - pip install toml ')
        with open(file, 'r') as f:
            return toml.load(f)

    @staticmethod
    def save(obj, file):
        with open(file, 'r') as f:
            return toml.dump(obj, file)