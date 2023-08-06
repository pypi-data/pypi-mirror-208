import typing, abc
from System import Action_2, Exception, Array_1, Action_1, Func_1, IDisposable, Random
from System.Collections.Generic import IEnumerable_1, Dictionary_2, List_1, HashSet_1, IList_1
from TransformsAI.Animo.Numerics import Vector2Int

class AnimoLogger(abc.ABC):
    StandardLogger : Action_2[typing.Any, AnimoLogger.LogType]
    @staticmethod
    def Log(message: typing.Any) -> None: ...
    @staticmethod
    def LogError(message: typing.Any) -> None: ...
    @staticmethod
    def LogException(exception: Exception) -> None: ...
    @staticmethod
    def LogWarning(message: typing.Any) -> None: ...
    @staticmethod
    def RegisterLogger(printLog: Action_2[typing.Any, AnimoLogger.LogType]) -> None: ...

    class LogType(typing.SupportsInt):
        @typing.overload
        def __init__(self, value : int) -> None: ...
        @typing.overload
        def __init__(self, value : int, force_if_true: bool) -> None: ...
        def __int__(self) -> int: ...
        
        # Values:
        Info : AnimoLogger.LogType # 0
        Warning : AnimoLogger.LogType # 1
        Error : AnimoLogger.LogType # 2
        Exception : AnimoLogger.LogType # 3



class EnumUtils_GenericClasses(abc.ABCMeta):
    Generic_EnumUtils_GenericClasses_EnumUtils_1_T = typing.TypeVar('Generic_EnumUtils_GenericClasses_EnumUtils_1_T')
    def __getitem__(self, types : typing.Type[Generic_EnumUtils_GenericClasses_EnumUtils_1_T]) -> typing.Type[EnumUtils_1[Generic_EnumUtils_GenericClasses_EnumUtils_1_T]]: ...

EnumUtils : EnumUtils_GenericClasses

EnumUtils_1_T = typing.TypeVar('EnumUtils_1_T')
class EnumUtils_1(typing.Generic[EnumUtils_1_T], abc.ABC):
    Values : Array_1[EnumUtils_1_T]


class IEnumerableExtensions(abc.ABC):
    # Skipped ForEach due to it being static, abstract and generic.

    ForEach : ForEach_MethodGroup
    class ForEach_MethodGroup:
        def __getitem__(self, t:typing.Type[ForEach_1_T1]) -> ForEach_1[ForEach_1_T1]: ...

        ForEach_1_T1 = typing.TypeVar('ForEach_1_T1')
        class ForEach_1(typing.Generic[ForEach_1_T1]):
            ForEach_1_T = IEnumerableExtensions.ForEach_MethodGroup.ForEach_1_T1
            def __call__(self, ts: IEnumerable_1[ForEach_1_T], action: Action_1[ForEach_1_T]) -> None:...




class Pool_GenericClasses(abc.ABCMeta):
    Generic_Pool_GenericClasses_Pool_1_T = typing.TypeVar('Generic_Pool_GenericClasses_Pool_1_T')
    def __getitem__(self, types : typing.Type[Generic_Pool_GenericClasses_Pool_1_T]) -> typing.Type[Pool_1[Generic_Pool_GenericClasses_Pool_1_T]]: ...

Pool : Pool_GenericClasses

Pool_1_T = typing.TypeVar('Pool_1_T')
class Pool_1(typing.Generic[Pool_1_T]):
    def __init__(self, instantiate: Func_1[Pool_1_T], initialCount: int = ...) -> None: ...
    def Lease(self) -> Pool_1_T: ...
    def Recycle(self, obj: Pool_1_T) -> None: ...


class PooledDict_GenericClasses(abc.ABCMeta):
    Generic_PooledDict_GenericClasses_PooledDict_2_TKey = typing.TypeVar('Generic_PooledDict_GenericClasses_PooledDict_2_TKey')
    Generic_PooledDict_GenericClasses_PooledDict_2_TValue = typing.TypeVar('Generic_PooledDict_GenericClasses_PooledDict_2_TValue')
    def __getitem__(self, types : typing.Tuple[typing.Type[Generic_PooledDict_GenericClasses_PooledDict_2_TKey], typing.Type[Generic_PooledDict_GenericClasses_PooledDict_2_TValue]]) -> typing.Type[PooledDict_2[Generic_PooledDict_GenericClasses_PooledDict_2_TKey, Generic_PooledDict_GenericClasses_PooledDict_2_TValue]]: ...

PooledDict : PooledDict_GenericClasses

PooledDict_2_TKey = typing.TypeVar('PooledDict_2_TKey')
PooledDict_2_TValue = typing.TypeVar('PooledDict_2_TValue')
class PooledDict_2(typing.Generic[PooledDict_2_TKey, PooledDict_2_TValue], IDisposable):
    @property
    def Dict(self) -> Dictionary_2[PooledDict_2_TKey, PooledDict_2_TValue]: ...
    @Dict.setter
    def Dict(self, value: Dictionary_2[PooledDict_2_TKey, PooledDict_2_TValue]) -> Dictionary_2[PooledDict_2_TKey, PooledDict_2_TValue]: ...
    @staticmethod
    def Acquire() -> PooledDict_2[PooledDict_2_TKey, PooledDict_2_TValue]: ...
    def Dispose(self) -> None: ...


class PooledList_GenericClasses(abc.ABCMeta):
    Generic_PooledList_GenericClasses_PooledList_1_T = typing.TypeVar('Generic_PooledList_GenericClasses_PooledList_1_T')
    def __getitem__(self, types : typing.Type[Generic_PooledList_GenericClasses_PooledList_1_T]) -> typing.Type[PooledList_1[Generic_PooledList_GenericClasses_PooledList_1_T]]: ...

PooledList : PooledList_GenericClasses

PooledList_1_T = typing.TypeVar('PooledList_1_T')
class PooledList_1(typing.Generic[PooledList_1_T], IDisposable):
    @property
    def List(self) -> List_1[PooledList_1_T]: ...
    @List.setter
    def List(self, value: List_1[PooledList_1_T]) -> List_1[PooledList_1_T]: ...
    @staticmethod
    def Acquire() -> PooledList_1[PooledList_1_T]: ...
    def Dispose(self) -> None: ...


class PooledSet_GenericClasses(abc.ABCMeta):
    Generic_PooledSet_GenericClasses_PooledSet_1_T = typing.TypeVar('Generic_PooledSet_GenericClasses_PooledSet_1_T')
    def __getitem__(self, types : typing.Type[Generic_PooledSet_GenericClasses_PooledSet_1_T]) -> typing.Type[PooledSet_1[Generic_PooledSet_GenericClasses_PooledSet_1_T]]: ...

PooledSet : PooledSet_GenericClasses

PooledSet_1_T = typing.TypeVar('PooledSet_1_T')
class PooledSet_1(typing.Generic[PooledSet_1_T], IDisposable):
    @property
    def Set(self) -> HashSet_1[PooledSet_1_T]: ...
    @Set.setter
    def Set(self, value: HashSet_1[PooledSet_1_T]) -> HashSet_1[PooledSet_1_T]: ...
    @staticmethod
    def Acquire() -> PooledSet_1[PooledSet_1_T]: ...
    def Dispose(self) -> None: ...


class RandomUtils(abc.ABC):
    @classmethod
    @property
    def Instance(cls) -> Random: ...
    @staticmethod
    def RandomDirection() -> Vector2Int: ...
    # Skipped Pick due to it being static, abstract and generic.

    Pick : Pick_MethodGroup
    class Pick_MethodGroup:
        def __getitem__(self, t:typing.Type[Pick_1_T1]) -> Pick_1[Pick_1_T1]: ...

        Pick_1_T1 = typing.TypeVar('Pick_1_T1')
        class Pick_1(typing.Generic[Pick_1_T1]):
            Pick_1_T = RandomUtils.Pick_MethodGroup.Pick_1_T1
            @typing.overload
            def __call__(self, array: Array_1[Pick_1_T]) -> typing.Optional[Pick_1_T]:...
            @typing.overload
            def __call__(self, list: IList_1[Pick_1_T]) -> typing.Optional[Pick_1_T]:...


    # Skipped Shuffle due to it being static, abstract and generic.

    Shuffle : Shuffle_MethodGroup
    class Shuffle_MethodGroup:
        def __getitem__(self, t:typing.Type[Shuffle_1_T1]) -> Shuffle_1[Shuffle_1_T1]: ...

        Shuffle_1_T1 = typing.TypeVar('Shuffle_1_T1')
        class Shuffle_1(typing.Generic[Shuffle_1_T1]):
            Shuffle_1_T = RandomUtils.Shuffle_MethodGroup.Shuffle_1_T1
            def __call__(self, list: IList_1[Shuffle_1_T]) -> None:...



