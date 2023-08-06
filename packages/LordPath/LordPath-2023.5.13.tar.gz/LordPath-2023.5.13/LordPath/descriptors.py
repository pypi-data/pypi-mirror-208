from pathlib import Path


class PathDescriptor:
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        value = getattr(instance, self.private_name, None)
        return value

    def __set__(self, instance, value):
        if isinstance(value, str):
            value = Path(value)
        elif isinstance(value, (int, float)):
            value = Path(str(value))
        setattr(instance, self.private_name, value)
