# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from typing import Any, Sequence, SupportsIndex,  Type, TypeVar, Union
import numpy as np
from numpy.typing import NDArray


ScalarType = TypeVar("ScalarType", bound=np.generic)

ShapeLike = Union[SupportsIndex, Sequence[SupportsIndex]]

def zeros(shape: ShapeLike, dtype: Type[ScalarType]) -> NDArray[ScalarType]:
    return np.zeros(shape=shape, dtype=dtype)

def ones(shape: ShapeLike, dtype: Type[ScalarType]) -> NDArray[ScalarType]:
    return np.ones(shape=shape, dtype=dtype)

def array(object: Any, dtype: Type[ScalarType]) -> NDArray[ScalarType]:
    return np.array(object, dtype=dtype)

def expand_dims(a: NDArray[ScalarType], axis:int) -> NDArray[ScalarType]:
    return np.expand_dims(a, axis=axis)

def multiply(object: NDArray[ScalarType], other:Union[int,float]) -> NDArray[ScalarType]:
    return np.multiply(object, other)
