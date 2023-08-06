import shutil
from pathlib import Path
# pip install regex
import regex as re
from typing import Union

# File Path
patternFileName = re.compile(r'[\/\\\?\<\>\|\:\'\"\*,]')  # / \ ? < > | : ' " * ,

# configs
encodes = ["utf-8-sig", "utf-8", "utf-16", "cp1252", "iso8859-1", "cp437"]
list_dir_filter = ['.DS_Store', '.git']


def _path_convert(path: str | Path) -> Path:
    if isinstance(path, str):
        return Path(path)
    else:
        return path


def listdir(path, *, only_files=False, only_folders=False, as_fullpath=False):
    path = _path_convert(path)

    file_list = [f for f in path.iterdir() if f.name not in list_dir_filter]

    if only_files:
        file_list = [f for f in file_list if f.is_file()]
    if only_folders:
        file_list = [f for f in file_list if f.is_dir()]

    return file_list


def mkdir(*path):
    for p in path:
        p = _path_convert(p)
        p.mkdir(parents=True, exist_ok=True)


def makedirs(*path):
    mkdir(*path)


def clear_empty_folder(path, recursive=False):
    path_obj = Path(path)

    # Find all subdirectories of the given path that don't match any filter and iterate over them.
    folders = [subdir for subdir in path_obj.iterdir() if
               subdir.is_dir() and not any(str(subdir).endswith(i) for i in list_dir_filter)]

    # Check if each subdirectory is empty and delete it, if empty.
    for folder in folders:
        if recursive:
            clear_empty_folder(folder, True)
        files = list(folder.iterdir())
        files = [f for f in files if f.name not in ['.DS_Store']]
        if not any(files):
            shutil.rmtree(folder)


def file_name_check(file_name):
    return patternFileName.sub('', file_name)


def path_check(path: Path | str) -> Path:
    """
    Replace illegal characters in file / folder path
    """
    if not isinstance(path, str):
        path = str(path)

    folders = re.split(r"[\\/]", path)
    for i in range(0, len(folders)):
        f = folders[i]
        if i == 0:
            if len(f) == 2 and ":" in f:
                continue
        f = str(file_name_check(f))
        folders[i] = f

    return Path(path)


# save load Files

typical_readable_file_endings = {
    '.txt',
    '.nfo',
    '.html',
    '.md'
}


def read_file(file: Union[str, list, Path], default=None):
    """
    :param file: file to be loaded. Specification as list to indicate alternative files
    :param default: default return
    """
    if isinstance(file, list):
        for f in file:
            _text = read_file(f)
            if _text:
                return _text

    file = Path(file)
    if not file.exists():
        return default

    with file.open("br") as f:
        read_binary = f.read()

    for enc in encodes:
        try:
            d = read_binary.decode(enc)
            if 'Û' in d:
                char_position = d.index('Û')
                if read_binary[char_position] == 219:  # 219 (=/xdb) welcher bei 1252 ein falsches zeichen ist
                    continue
            return d
        except UnicodeDecodeError:
            pass

    return default


def typical_readable_file_type(filename):
    path = Path(filename)
    return path.suffix in typical_readable_file_endings


# file

def save_file(file, text):

    file: Path = path_check(file)
    dir_path = file.parent
    if not dir_path.exists():
        makedirs(dir_path)
    with file.open("w", encoding=encodes[0]) as f:
        f.write(text)
    return True
