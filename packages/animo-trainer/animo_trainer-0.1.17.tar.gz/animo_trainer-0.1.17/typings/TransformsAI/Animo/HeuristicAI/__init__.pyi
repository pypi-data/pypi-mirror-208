import typing, abc
from TransformsAI.Animo.Objects import CharacterActions, Character, TypeIds
from System import Predicate_1
from TransformsAI.Animo.Grid import GridObject

class HeuristicBehaviourExtensions(abc.ABC):
    RandomRotationFrequency : float
    @staticmethod
    def ChopAllTrees(character: Character, targetAnimoOnMissingTarget: bool) -> CharacterActions: ...
    @staticmethod
    def CrystalDestroyer(character: Character, targetAnimoOnMissingTarget: bool) -> CharacterActions: ...
    @staticmethod
    def DecideAction(autoBehaviour: HeuristicBehaviours, character: Character) -> CharacterActions: ...
    @staticmethod
    def MoveRandomly(character: Character) -> CharacterActions: ...
    @staticmethod
    def UseOnTargetWithTool(character: Character, grabTarget: TypeIds, targetDiscriminant: Predicate_1[GridObject], targetAnimoOnMissingTarget: bool) -> CharacterActions: ...
    @staticmethod
    def WaterWiltedFlowers(character: Character, targetAnimoOnMissingTarget: bool) -> CharacterActions: ...


class HeuristicBehaviours(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...
    
    # Values:
    StandStill : HeuristicBehaviours # 0
    MoveRandomly : HeuristicBehaviours # 1
    ChopTreesWithAxe : HeuristicBehaviours # 2
    WaterAllFlowers : HeuristicBehaviours # 3
    CrystalDestroyer : HeuristicBehaviours # 4

