import base64
import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any


def trailing_join(iter: list[str], join_string: str, trail_if_len_gt: int = 0) -> str:
    
    return join_string.join(iter)+ join_string * (len(iter) > trail_if_len_gt)
    
class sflist(list[str]):
    """
    A pyhton list representation of a HLD list.
    """
    
    @classmethod
    def from_string(cls, string: str):
        return cls(string.split("+")[:-1])
    def to_string(self) -> str:
        return trailing_join(self, "+")

class sfdict(dict[str, list[str]]):
    """
    A pyhton dict representation of a HLD dict.
    """

    @classmethod
    def from_string(cls, string: str):
        to_return = {}
        pairs = string.split(">")
        for pair in pairs[:-1]:
            s_pair = pair.split("=")
            key = s_pair[0]
            value = s_pair[1].split("&")
            if len(value) > 1: value = value[:-1]
            to_return[key] = value
        return cls(**to_return)
    def to_string(self) -> str:
        return trailing_join([f"{key}={trailing_join(value, '&')}" for key, value in self.items() if value], ">")

@dataclass
class HLDSaveFile:
    """
    A python representation of a savefile.

    For field documentation please consult tihs: https://github.com/springsylvi/HLD-Save-Editor/blob/master/save_format.txt
    """
    badass: float
    mapMod: sfdict
    dateTime: float
    healthUp: float
    cl: sfdict
    destruct: sfdict
    values: sfdict
    gunReminderTimes: float
    fireplaceSave: float
    checkHP: float
    compShell: float
    cSwords: sflist
    cape: float
    halluc: float
    newcomerHoardeMessageShown: float
    tutHeal: float
    noSpawn: sflist
    checkY: float
    specialUp: float
    checkBat: float
    noviceMode: float
    successfulHealTimes: float
    cCapes: sflist
    CH: float
    gear: float
    checkCID: float
    rooms: sflist
    permaS: sfdict
    checkRoom: float
    wellMap: sflist
    cShells: sflist
    eq01: float
    tablet: sflist
    successfulWarpTimes: float
    skill: sflist
    bosses: sfdict
    scK: sfdict
    warp: sflist
    hasMap: float
    events: sflist
    gearReminderTimes: float
    enemies: sfdict
    scUp: sflist
    checkX: float
    bossGearbits: sflist
    cues: sflist
    playT: float
    well: sflist
    sc: sflist
    drifterkey: float
    successfulCollectTimes: float
    checkAmmo: float
    checkStash: float
    charDeaths: float
    eq00: float
    healthKits: sflist
    sword: float
    gameName: str

    header: str

    @classmethod
    def _auto_type(cls, value: Any, strtype) -> sfdict | sflist | float | str:
        strtype = strtype.__name__
        type_map = {
            "sfdict": sfdict.from_string,
            "sflist": sflist.from_string,
            "float": float,
            "str": str
        }
        return type_map[strtype](value)

    @classmethod
    def load(cls, path: str | Path):
        """
        Loads a savefile from path.
        """
        with open(path, "r") as in_:
            text = in_.read()
            return cls.from_string(text)

    @classmethod
    def from_string(cls, string: str):
        """
        Creates a savefile from an encoded string.
        """
        save_dict: dict = json.loads(
            base64.standard_b64decode(string[80:])[:-1]
        )
    
        if not "eq00" in save_dict: save_dict["eq00"] = 0.
        if not "eq01" in save_dict: save_dict["eq01"] = 0.
        save_dict["header"] = string[:80]

        for field in fields(cls):
            save_dict[field.name] = cls._auto_type(save_dict[field.name], field.type)  
        return cls(**save_dict)

    def dump(self, path: str | Path) -> None:
        """
        Dumps the savefile to path.
        """
        with open(path, "w") as out:
            out.write(self.to_string())
    
    def to_string(self) -> str:
        """
        Gets the encoded string from the savefile.
        """
        jsoned, header = self.to_json_string(indent=0)
        encoded_body = header + str(base64.standard_b64encode(bytes(jsoned + "\x00", "utf8")) , "utf-8")
        return encoded_body
    
    def to_json_string(self, indent: int = 0) -> tuple[str, str]:
        """
        An inbetween step for to_string(). Can be used for debugging.
        """
        save_dict = self.__dict__.copy()
        header = save_dict.pop("header")
        for key, value in save_dict.items():
            if isinstance(value, (sfdict, sflist)): save_dict[key] = value.to_string()
        if save_dict["eq00"] == 0.: save_dict.pop("eq00")
        if save_dict["eq01"] == 0.: save_dict.pop("eq01")
        return (json.dumps(save_dict, indent=indent), header)

    def debug_dump(self, path: str | Path) -> None:
        """
        Dumps an unencoded savefile to path.
        """
        with open(path, "w") as out:
            jsoned, _ = self.to_json_string(indent=4)
            out.write(jsoned)
