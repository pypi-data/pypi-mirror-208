from pathlib import Path

from LordPath import read_file, typical_readable_file_type
from LordPath import listdir, makedirs
from LordPath.opener import open_by_type
from LordPath.dataset import ending_to_file_type
from LordUtils.decorators import CachedProperty

# LordThings
from LordUtils import fn_match_value


class FileClass(object):
    type = 'file'

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.file_type = ending_to_file_type.get(self.ending, 'unknown')

        self._open = None
        self._text = None

    def open(self):
        if self._open is None:
            self._open = open_by_type(self.path, ending=self.ending)
        return self._open

    @property
    def filename(self):
        return self.path.name

    @property
    def name(self):
        return self.path.stem

    @property
    def extension(self):
        """Alias zu ending"""
        return self.ending

    @property
    def ending(self):
        """Alias zu ending"""
        return self.path.suffix.replace('.', '')

    @property
    def full_name(self):
        return self.path.name

    @property
    def data(self):
        return self.open()

    @property
    def text(self):
        if self._text is None:
            self._text = self.get_text()
        return self._text

    def get_text(self, only_typical=False):
        if only_typical is False or typical_readable_file_type(self.filename):
            r = read_file(self.path)
        else:
            r = '...'
        return r

    def to_json(self):
        return {
            'path': '--CENSORED--',
            'filename': self.filename,
            'name': self.name,
            'text': self.get_text(only_typical=True),
            'ending': self.ending,
            'file_type': self.file_type,
            'type': self.type,
            'data': self.data,
            '__class__': self.__class__.__name__
        }

    def move(self, target_path):
        target_path = Path(target_path)
        if not target_path.exists():
            makedirs(target_path)

        new_path = target_path / self.filename
        self.path = self.path.rename(new_path)

    def __str__(self):
        return self.filename

    def __getitem__(self, key):  # => self[key]
        return self.__getattribute__(key)


class FolderClass(object):
    type = "folder"

    def __init__(self, path):
        self.path = Path(path)

    @property
    def name(self):
        return self.path.name

    @CachedProperty
    def elements(self):
        elements = []
        _p = self.path
        for f in listdir(_p):
            f = create_from_path(f)
            elements.append(f)
        return elements

    @property
    def full_name(self):
        return self.name

    @property
    def all_files(self):
        for f in self.elements:
            if isinstance(f, FolderClass):
                yield from f.all_files
            else:
                yield f

    @property
    def files(self):
        return [f for f in self.elements if isinstance(f, FileClass)]

    @property
    def folders(self):
        return [f for f in self.elements if isinstance(f, FolderClass)]

    def to_json(self):
        return {
            # todo make censor setting for this
            'path': '--CENSORED--',
            'name': self.name,
            'type': self.type,
            '__class__': self.__class__.__name__
        }

    def search(self, *q: str | list):
        # check files
        for f in self.files:
            if fn_match_value(str(f), q):
                yield f
        for f in self.folders:
            yield from f.search(*q)

    def search_one(self, *q):
        for f in self.search(*q):
            return f

    def move(self, target_path):
        target_path = Path(target_path)
        if not target_path.exists():
            makedirs(target_path)

        new_path = target_path / self.name
        self.path = self.path.rename(new_path)

    def __str__(self):
        return self.name

    def __iter__(self):
        return iter(self.elements)

    def __reversed__(self):
        return reversed(self.elements)

    def __getitem__(self, key):  # => self[key]
        return self.__getattribute__(key)


class VirtualFolderClass(object):
    type = "virtual-folder"

    def __init__(self, name=None):
        self.name = name
        self.elements: list[FileClass, FolderClass] = []

    def add(self, *elements: FolderClass | FileClass):
        for e in elements:
            self.elements.append(e)

    def remove(self, *elements: FolderClass | FileClass):
        for e in elements:
            if e in self.elements:
                self.elements.remove(e)

    @classmethod
    def init_from_folder(cls, path):
        path = Path()
        name = path.name
        v = cls(name)
        for f in path.iterdir():
            f = create_from_path(f)
            v.add(f)

    @property
    def files(self):
        return [f for f in self.elements if isinstance(f, FileClass)]

    @property
    def folders(self):
        return [f for f in self.elements if isinstance(f, FolderClass)]

    @property
    def all_files(self):
        for f in self.elements:
            if isinstance(f, FolderClass):
                yield from f.all_files
            else:
                yield f

    def to_json(self):
        return {
            'name': self.name,
            'type': self.type,
            '__class__': self.__class__.__name__,
            'files': self.files,
            'folders': self.folders
        }

    def search(self, *q: str):
        # check files
        for f in self.files:
            if fn_match_value(str(f), q):
                yield f
        for f in self.folders:
            yield from f.search(*q)

    def search_one(self, *q):
        for f in self.search(*q):
            return f

    def move(self, target_path):
        for e in self.elements:
            e.move(target_path)

    def __iter__(self):
        return iter(self.elements)

    def __reversed__(self):
        return reversed(self.elements)


vffc_type = FileClass | FolderClass | VirtualFolderClass
# vffc => virtual file folder class


def create_from_path(path: str | Path):
    path = Path(path)

    if path.is_file():
        return FileClass(path)
    elif path.is_dir():
        return FolderClass(path)
    else:
        return None
