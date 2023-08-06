
from abc import ABC, abstractmethod


class Opener(ABC):
    compatible_endings = []

    @classmethod
    def check(cls, ending):
        return ending in cls.compatible_endings

    @staticmethod
    @abstractmethod
    def load(file):
        pass

    @staticmethod
    @abstractmethod
    def save(obj, file):
        pass