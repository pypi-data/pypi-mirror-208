from pathlib import Path
from hldlib.hldlevel import HLDLevel, HLDHolder
from hldlib.hlderror import HLDError
from hldlib.hlddirections import HLDDirection
from typing import Iterable
import os

def find_path(textfile_name: str = "hlddir.txt", where_to_search: str | Path = ".") -> str:
    """
    An easy way to retrive a stored path. Searches in the specified directory and all subdirectories.
    """
    for dir_path, _, file_names in os.walk(where_to_search):
        for file_name in file_names:
            if file_name.lower() == textfile_name:
                with open(os.path.join(dir_path, file_name)) as hld_dir_file:
                    return hld_dir_file.readline().rstrip()
    raise HLDError(f"No {textfile_name} found.")

def get_levels(path: str | Path, dirs: Iterable[str]):
    for directory in dirs:
        for level in [level for level in os.listdir(os.path.join(path, directory)) if level.endswith(".lvl")]:
            filepath: str = os.path.join(path, directory, level)
            yield filepath, directory, level

def default_load(path: str | Path) -> HLDHolder:
    """
    Default load method for loading levels from the basic HLD .lvl file structure.
    
    Gets all levels from path/North, path/East, path/..., path/Abyss
    """
    loaded = HLDHolder()
    for level_path, _, _ in get_levels(path, HLDDirection):
        lvl = HLDLevel.load(level_path)
        loaded.append(lvl)
    return loaded

class Counter:
    """
    A simple counter class. Useful for creating new HLDObj's and giving them unique IDs.
    """
    def __init__(self, val: int = 10000):
        self._val = val

    def use(self) -> int:
        self._val += 1
        return self._val
