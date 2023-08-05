import os
from pathlib import Path
import re
from hldlib.hldobjects import HLDObj, _int_float_str_convert
from hldlib.hlddirections import HLDDirection
from hldlib.hlderror import HLDError


class HLDLevel:
    """
    A python representation of a HLD level.
    """

    def __init__(self, name: str, date: float, layer_names: dict, room_settings: dict, objects: list[HLDObj], direction: HLDDirection) -> None:
        self.name = name
        self.date = date
        self.layer_names = layer_names
        self.room_settings = room_settings
        self.objects = objects
        self.direction = direction
    
    @classmethod
    def load(cls, path: str | Path, direction: HLDDirection | None = None):
        """
        Loads a level from path. If the direction is not set, uses the directory name as direction.
        """
        name = os.path.basename(path)
        if not direction:
            direction = HLDDirection(os.path.basename(os.path.dirname(path)))
        with open(path, "r") as f:
            return cls.from_string(f.read(), name, direction)

    @classmethod    
    def from_string(cls, string: str, name: str, direction: HLDDirection):
        """
        Loads a level from a string.
        """
        lines = string.split("\n")
        layer_names = {}
        room_settings = {}
        objects = []
        i = 0

        while not (match := re.match(r"(?:DATE|VERSION),(?P<date>.*?),", lines[i])): i += 1
        date = float(match.group("date")); i += 1
        while not (match := re.search(r"layerName,(?P<id>.*?),(?P<name>.*?),", lines[i])): i += 1
        while (match := re.search(r"layerName,(?P<id>.*?),(?P<name>.*?),", lines[i])):
            layer_names[int(match.group("id"))] = match.group("name")
            i += 1
        while not (match := re.search(r",floorSpr,", lines[i])): i += 1
        split_line = list(map(_int_float_str_convert, lines[i].lstrip().split(",")[:-1]))
        sketch = split_line[-4:]
        rest_of_settings = iter(split_line[:-4])
        for x in rest_of_settings:
            room_settings[x] = next(rest_of_settings)
        room_settings[sketch[0]] = [sketch[1], sketch[2], sketch[3]]
        i += 1
        for line in lines[i:]:
            if re.search(r"obj,.*?,.*?,", line): objects.append(HLDObj.from_string(line))
        
        return cls(date=date, layer_names=layer_names, room_settings=room_settings, objects=objects, name=name, direction=direction)
    

    def dump(self, path: str | Path) -> None:
        """
        Dumps the level to path. Uses levels name as the dumped file name.
        """
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, self.name), "w") as file:
            file.write(self.to_string())
    
    def to_string(self) -> str:
        """
        Gets the level in a string form. Can be used to write to a file.
        """
        return f"DATE,{self.date}," +\
                "\n\t " + "\n\t ".join([f"layerName,{key},{value}," for key, value in self.layer_names.items()]) +\
                "\n\t " + ",".join([f"{key},{value}" for key, value in self.room_settings.items() if key != "sketchalpha"]) +\
                    f",sketchalpha,{','.join(list(map(str, self.room_settings['sketchalpha'])))}," +\
                "".join([obj.to_string() for obj in self.objects])
    

    def __eq__(self, other) -> bool:
        if other.__class__ is not self.__class__: return False
        return self.__dict__ == other.__dict__


class HLDHolder(list[HLDLevel]):
    """
    A convenient list for levels with the ability to dump all levels.
    """
    def dump_all(self, path: str) -> None:
        """
        Dumps all levels.

        NOTE: uses level direction as the dump directory name.
        So dump_all(path) will dump all levels with direction HLDDirection.NORTH in path/North
        """
        for level in self:
            level.dump(os.path.join(path, level.direction))

level_names_and_ids: list[tuple[str, int]] = [
    ("rm_IN_01_brokenshallows.lvl", 46),
    ("rm_IN_02_Tutorial.lvl", 47),
    ("rm_IN_03_Tut_Combat.lvl", 48),
    ("rm_IN_HorizonCliff.lvl", 49),
    ("rm_IN_HalucinationDeath.lvl", 50),
    ("rm_IN_Drifterfire.lvl", 51),
    ("rm_IN_BlackWaitRoom.lvl", 52),
    ("rm_IN_BackerTablet.lvl", 53),
    ("rm_INL_Secrets.lvl", 55),
    ("rm_LIN_Gaps.lvl", 56),
    ("rm_LIN_Combat.lvl", 57),
    ("rm_C_DrifterWorkshop.lvl", 60),
    ("rm_C_Central.lvl", 61),
    ("rm_C_Dregs_N.lvl", 62),
    ("rm_C_Dregs_S.lvl", 63),
    ("rm_C_Dregs_E.lvl", 64),
    ("rm_C_Dregs_W.lvl", 65),
    ("rm_C_Ven_Apoth.lvl", 66),
    ("rm_C_Ven_Dash.lvl", 67),
    ("rm_C_Ven_Gun.lvl", 68),
    ("rm_C_Ven_Spec.lvl", 69),
    ("rm_C_Ven_SDojo.lvl", 70),
    ("rm_CArena.lvl", 71),
    ("rm_PAX_Staging.lvl", 72),
    ("rm_PAX_arena1.lvl", 73),
    ("rm_PAX_arena2.lvl", 74),
    ("rm_PAX_arenaE.lvl", 75),
    ("rm_PAX_arenaW.lvl", 76),
    ("rm_PAX_arenaAll.lvl", 77),
    ("rm_C_BackerTabletX.lvl", 78),
    ("rm_TelevatorShaft.lvl", 79),
    ("rm_NL_EntrancePath.lvl", 84),
    ("rm_NX_TitanVista.lvl", 85),
    ("rm_NX_NorthHall.lvl", 86),
    ("rm_NL_CaveVAULT.lvl", 87),
    ("rm_NX_AfterTitan.lvl", 88),
    ("rm_NC_NPCHatchery.lvl", 89),
    ("rm_NX_ShrinePath.lvl", 90),
    ("rm_NL_ShrinePath2VAULT.lvl", 91),
    ("rm_NX_Cave01.lvl", 92),
    ("rm_NX_ShrinePath_2.lvl", 93),
    ("rm_NX_MoonCourtyard.lvl", 94),
    ("rm_NX_TowerLock.lvl", 95),
    ("rm_NC_CliffCampfire.lvl", 96),
    ("rm_NL_ToBrokenShallows.lvl", 97),
    ("rm_NX_Stairs03.lvl", 98),
    ("rm_NL_WarpRoom.lvl", 100),
    ("rm_NL_CrushWarpHall.lvl", 101),
    ("rm_NL_CrushTransition.lvl", 102),
    ("rm_NL_CrushBackLoop.lvl", 103),
    ("rm_NC_CrushArena.lvl", 104),
    ("rm_NL_DropSpiralOpen.lvl", 106),
    ("rm_NL_DropPits.lvl", 107),
    ("rm_NL_DropBlockCultFight.lvl", 108),
    ("rm_NL_DropArena.lvl", 109),
    ("rm_NL_GapOpening.lvl", 111),
    ("rm_NX_GapWide.lvl", 112),
    ("rm_NL_GapHallway.lvl", 113),
    ("rm_NL_RisingArena.lvl", 114),
    ("rm_NX_CathedralEntrance.lvl", 116),
    ("rm_NX_CathedralHall.lvl", 117),
    ("rm_NL_AltarThrone.lvl", 118),
    ("rm_NX_SpiralStaircase.lvl", 119),
    ("rm_NX_LibrarianTablet.lvl", 120),
    ("rm_NX_JerkPope.lvl", 121),
    ("rm_NL_StairAscent.lvl", 123),
    ("rm_NL_CrushArena.lvl", 124),
    ("rm_SX_SouthOpening.lvl", 128),
    ("rm_CH_CTemplate.lvl", 129),
    ("rm_SX_TowerSouth.lvl", 130),
    ("rm_SX_NPC.lvl", 131),
    ("rm_S_Gauntlet_Elevator.lvl", 132),
    ("rm_CH_BGunPillars.lvl", 133),
    ("rm_CH_BFinal.lvl", 134),
    ("rm_S_GauntletEnd.lvl", 135),
    ("rm_CH_BDirkDemolition.lvl", 137),
    ("rm_CH_TABigOne.lvl", 139),
    ("rm_CH_CGateBlock.lvl", 140),
    ("rm_CH_BMadDash.lvl", 141),
    ("rm_CH_TLongestRoad.lvl", 142),
    ("rm_S_BulletBaker.lvl", 143),
    ("rm_CH_CEndHall.lvl", 144),
    ("rm_CH_CTurnHall.lvl", 146),
    ("rm_CH_Bfps.lvl", 147),
    ("rm_CH_CBigggns.lvl", 148),
    ("rm_CH_CSpawnGround.lvl", 149),
    ("rm_S_CountAculard.lvl", 150),
    ("rm_CH_ACorner.lvl", 152),
    ("rm_CH_BDirkDeluge.lvl", 154),
    ("rm_CH_BPods.lvl", 155),
    ("rm_CH_BGunDirkDash.lvl", 156),
    ("rm_S_MarkScythe.lvl", 157),
    ("rm_S_GauntletLinkup.lvl", 158),
    ("rm_CH_APillarBird.lvl", 160),
    ("rm_CH_CSpiral.lvl", 161),
    ("rm_CH_TBirdStandoff.lvl", 162),
    ("rm_CH_BLeaperFall.lvl", 163),
    ("rm_S_BennyArrow.lvl", 164),
    ("rm_S_GauntletTitanFinale.lvl", 165),
    ("rm_EA_EastOpening.lvl", 171),
    ("rm_EC_SwordBridge.lvl", 172),
    ("rm_EL_FlameElevatorEnter.lvl", 173),
    ("rm_EA_WaterTunnelLAB.lvl", 174),
    ("rm_EC_ThePlaza.lvl", 175),
    ("rm_EC_NPCDrugDen.lvl", 176),
    ("rm_EX_TowerEast.lvl", 177),
    ("rm_EB_BogStreet.lvl", 178),
    ("rm_EC_PlazaToLoop.lvl", 179),
    ("rm_EL_MegaHugeLAB.lvl", 181),
    ("rm_EB_MeltyMashArena.lvl", 182),
    ("rm_EB_FlamePitLAB.lvl", 183),
    ("rm_EL_FlameElevatorExit.lvl", 184),
    ("rm_EB_DeadOtterWalk.lvl", 185),
    ("rm_EC_PlazaAccessLAB.lvl", 187),
    ("rm_EC_DocksLab.lvl", 188),
    ("rm_EX_DocksCampfire.lvl", 189),
    ("rm_EV_DocksBridge.lvl", 190),
    ("rm_EL_FrogArena.lvl", 191),
    ("rm_EC_BigBogLAB.lvl", 193),
    ("rm_EA_BogTempleCamp.lvl", 194),
    ("rm_EA_FrogBoss.lvl", 195),
    ("rm_EC_TempleIshVault.lvl", 196),
    ("rm_EC_EastLoop.lvl", 198),
    ("rm_EC_LoopLAB.lvl", 199),
    ("rm_EB_MeltyLeaperArena.lvl", 200),
    ("rm_EC_PlazaToDocks.lvl", 202),
    ("rm_EA_DockFightLab.lvl", 203),
    ("rm_EB_UnderOtterBigRifleRumble.lvl", 204),
    ("rm_EB_CleanersHole.lvl", 205),
    ("rm_WA_Entrance.lvl", 209),
    ("rm_WL_PrisonHALVAULT.lvl", 210),
    ("rm_WA_Deadwood.lvl", 211),
    ("rm_WA_DeadwoodS1.lvl", 212),
    ("rm_WA_Grotto_buffIntro.lvl", 213),
    ("rm_WC_WindingWood.lvl", 214),
    ("rm_WC_GrottoNPC.lvl", 215),
    ("rm_WL_NPCTreehouse.lvl", 216),
    ("rm_WC_MiniLab.lvl", 217),
    ("rm_WT_TheWood.lvl", 218),
    ("rm_WA_EntSwitch.lvl", 219),
    ("rm_WC_MeadowoodCorner.lvl", 220),
    ("rm_WB_TreeTreachery.lvl", 222),
    ("rm_WL_WestDrifterVault.lvl", 223),
    ("rm_WT_SlowLab.lvl", 225),
    ("rm_WC_CliffsideCellsRedux.lvl", 226),
    ("rm_WC_PrisonHAL.lvl", 227),
    ("rm_WC_ThinForest.lvl", 229),
    ("rm_WC_SimplePath.lvl", 230),
    ("rm_WC_CrystalLake.lvl", 231),
    ("rm_WC_CrystalLakeVault.lvl", 232),
    ("rm_WC_PrisonHallEnd.lvl", 233),
    ("rm_WC_ThinForestLow.lvl", 234),
    ("rm_WC_ThinForestLowSecret.lvl", 235),
    ("rm_WA_TitanFalls.lvl", 236),
    ("rm_WA_Vale.lvl", 238),
    ("rm_WC_BigMeadow.lvl", 239),
    ("rm_WC_BigMeadowVAULT.lvl", 240),
    ("rm_WC_MeadowCaveCrossing.lvl", 241),
    ("rm_WB_BigBattle.lvl", 242),
    ("rm_WB_TanukiTrouble.lvl", 243),
    ("rm_WC_RuinClearing.lvl", 244),
    ("rm_WX_Boss.lvl", 245),
    ("rm_WA_TowerEnter.lvl", 246),
    ("rm_WA_MultiEntranceLab.lvl", 247),
    ("rm_WA_CrsytalDescent.lvl", 248),
    ("rm_WA_GrottoX.lvl", 250),
    ("rm_WB_CrystalQueen.lvl", 251),
    ("rm_WT_ProtoGrid.lvl", 252),
    ("rm_WV_PuzzlePalaceNEW.lvl", 253),
    ("rm_A_ElevatorShaftUpper.lvl", 256),
    ("rm_A_ElevatorShaft.lvl", 257),
    ("rm_A_PreDownward.lvl", 258),
    ("rm_A_Downward.lvl", 259),
    ("rm_A_DownwardDead.lvl", 260),
    ("rm_A_DownwardDeadRevisit.lvl", 261),
    ("rm_A_EmberRoom.lvl", 262),
    ("rm_BossRush_Hub.lvl", 265),
    ("rm_BossRush_FrogBoss.lvl", 266),
    ("rm_BossRush_JerkPope.lvl", 267),
    ("rm_BossRush_General.lvl", 268),
    ("rm_BossRush_BulletBaker.lvl", 269),
    ("rm_BossRush_CountAculard.lvl", 270),
    ("rm_BossRush_MarkScythe.lvl", 271),
    ("rm_BossRush_BennyArrow.lvl", 272),
    ("rm_BossRush_Ember.lvl", 273),
    ("rm_C_DrifterWorkshop.lvl", 276)
]

def get_id_from_name(name: str) -> int:
    """
    A way to convert internal level ID to its name.
    """
    for namee, idd in level_names_and_ids:
        if namee == name: return idd
    raise HLDError(f"No such level named {name}.")

def get_name_from_id(id_: int) -> str:
    """
    A way to convert level name to its internal ID.
    """
    for namee, idd in level_names_and_ids:
        if idd == id_: return namee
    raise HLDError(f"No such level with id {id_}.")
