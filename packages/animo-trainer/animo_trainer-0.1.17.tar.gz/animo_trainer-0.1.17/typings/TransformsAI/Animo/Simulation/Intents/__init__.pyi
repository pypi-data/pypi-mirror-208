import typing, abc
from TransformsAI.Animo.Numerics import Vector3Int
from System.Collections.Generic import List_1
from TransformsAI.Animo.Grid import GridObject
from System import IComparable_1

class CharacterIntent(Intent):
    def __init__(self) -> None: ...
    ExecutionInfo : typing.Any
    GridItemUseTarget : typing.Optional[Vector3Int]
    HeldItemUseTarget : typing.Optional[Vector3Int]
    Positions : List_1[Vector3Int]
    Priority : int
    RelativeDirectionTarget : typing.Optional[Vector3Int]
    RelativeMoveTarget : typing.Optional[Vector3Int]
    WillGrab : bool
    @property
    def Source(self) -> GridObject: ...
    def Dispose(self) -> None: ...


class Intent(IComparable_1[Intent]):
    def __init__(self) -> None: ...
    ExecutionInfo : typing.Any
    Positions : List_1[Vector3Int]
    Priority : int
    @property
    def Source(self) -> GridObject: ...
    @Source.setter
    def Source(self, value: GridObject) -> GridObject: ...
    def CompareTo(self, other: Intent) -> int: ...
    def Dispose(self) -> None: ...
    # Skipped GetCharacterIntent due to it being static, abstract and generic.

    GetCharacterIntent : GetCharacterIntent_MethodGroup
    class GetCharacterIntent_MethodGroup:
        @typing.overload
        def __call__(self, source: GridObject, priority: int) -> CharacterIntent:...
        @typing.overload
        def __call__(self, source: GridObject, priority: int, position: Vector3Int) -> CharacterIntent:...

    # Skipped GetIntent due to it being static, abstract and generic.

    GetIntent : GetIntent_MethodGroup
    class GetIntent_MethodGroup:
        @typing.overload
        def __call__(self, source: GridObject, priority: int) -> Intent:...
        @typing.overload
        def __call__(self, source: GridObject, priority: int, position: Vector3Int) -> Intent:...



class IntentPriority(abc.ABC):
    CreateObject : int
    DeleteObject : int
    GrabObject : int
    MoveObject : int
    NeverConflict : int
    UseItem : int
    @staticmethod
    def GetPriority(type: typing.Type[typing.Any]) -> int: ...

