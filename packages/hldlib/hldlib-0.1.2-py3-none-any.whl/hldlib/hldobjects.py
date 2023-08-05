import re
from hldlib.hlderror import HLDError
from hldlib.hldtype import HLDType

class HLDObj:
    """
    A python representation of a HLD object.
    """

    def __init__(self, type: HLDType, x: int, y: int, uid: int, attrs: dict, dependencies: str = "-999999", layer: int = 0) -> None:
        self.type = type
        self.x = x
        self.y = y
        self.uid = uid
        self.attrs = attrs
        self.dependencies = dependencies
        self.layer = layer
    
    @classmethod
    def from_string(cls, line: str):
        """
        Creates an HLD object from a string as they are formated in level files.

        obj,Spawner,593,536,352,6,-999999,++,-1=dirk,-2=-999999,-4=1,-5=0,-6=-1,-7=0,-8=0,
        """
        regex_match = re.match(r"obj,(?P<type>.*?),(?P<uid>.*?),(?P<x>.*?),(?P<y>.*?),(?P<layer>.*?),(?P<dependencies>.*?),\+\+,(?P<attrs>.*)", line.strip().replace("//", ""))
        if not regex_match: raise HLDError(f"This line is not an HLDObject: {line}")
        type = regex_match.group("type")
        uid = int(regex_match.group("uid"))
        x = int(regex_match.group("x"))
        y = int(regex_match.group("y"))
        layer = int(regex_match.group("layer"))
        dependencies = regex_match.group("dependencies")
        attrs = {pair.split("=")[0]: _int_float_str_convert(pair.split("=")[1]) for pair in regex_match.group("attrs").split(",") if "=" in pair}
        return cls(type=HLDType(type), x=x, y=y, uid=uid, layer=layer, dependencies=dependencies, attrs=attrs)

    def to_string(self) -> str:
        """
        Gets the object in a string form as they are formated in level files.
        """
        attrs_to_str = ",".join([f"{key}={value}" for key, value in self.attrs.items()])
        return f"\n\t //obj,{self.type},{self.uid},{self.x},{self.y},{self.layer},{self.dependencies},++,{attrs_to_str},"
    
    def __eq__(self, other) -> bool:
        if other.__class__ is not self.__class__: return False
        return self.__dict__ == other.__dict__


def _int_float_str_convert(val: str) -> int | float | str:
    try: return int(val)
    except: pass
    try: return float(val)
    except: pass
    return val
