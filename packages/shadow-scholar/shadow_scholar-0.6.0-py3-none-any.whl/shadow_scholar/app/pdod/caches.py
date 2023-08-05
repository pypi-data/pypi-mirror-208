from abc import ABC, abstractmethod, abstractproperty
from enum import IntEnum
from typing import Any, Dict, Literal, Sequence, Union

from shadow_scholar.cli import safe_import

with safe_import():
    import numpy as np
    import torch
    from unqlite import UnQLite


TensorType = Union[torch.Tensor, np.ndarray]


class CacheMode(IntEnum):
    READ_ONLY = 1
    READ_WRITE = 4


class BaseTensorCache(ABC):
    def __init__(
        self,
        *args,
        mode: CacheMode = CacheMode.READ_WRITE,
        invalidate: bool = False,
        **kwargs,
    ) -> None:
        ...

    @abstractproperty
    def signature(self) -> str:
        ...

    @abstractmethod
    def write_many(self, keys: Sequence[str], values: Sequence[TensorType]):
        ...

    def write_one(self, key: str, value: TensorType):
        self.write_many([key], [value])

    @abstractmethod
    def read_many(self, keys: Sequence[str]) -> Sequence[TensorType]:
        ...

    def read_one(self, key: str) -> TensorType:
        return self.read_many([key])[0]
