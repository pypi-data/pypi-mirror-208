from __future__ import annotations

__all__ = ["BatchList"]

import copy
import math
from collections.abc import Iterable, Sequence
from typing import Any, TypeVar

import torch
from coola import objects_are_allclose, objects_are_equal
from torch import Tensor

from redcat.base import BaseBatch

T = TypeVar("T")
# Workaround because Self is not available for python 3.9 and 3.10
# https://peps.python.org/pep-0673/
TBatchList = TypeVar("TBatchList", bound="BatchList")


class BatchList(BaseBatch[list[T]]):
    r"""Implements a batch object to easily manipulate a list of
    examples.

    Args:
        data (list): Specifies the list of examples.
    """

    def __init__(self, data: list[T]) -> None:
        if not isinstance(data, list):
            raise TypeError(f"Incorrect type. Expect a list but received {type(data)}")
        self._data = data

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}(batch_size={self.batch_size:,})"

    @property
    def batch_size(self) -> int:
        return len(self._data)

    @property
    def data(self) -> list[T]:
        return self._data

    ###############################
    #     Creation operations     #
    ###############################

    def clone(self, *args, **kwargs) -> TBatchList:
        return self.__class__(copy.deepcopy(self._data))

    #################################
    #     Comparison operations     #
    #################################

    def allclose(
        self, other: Any, rtol: float = 1e-5, atol: float = 1e-8, equal_nan: bool = False
    ) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_allclose(
            self.data, other.data, rtol=rtol, atol=atol, equal_nan=equal_nan
        )

    def equal(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self.data, other.data)

    ###########################################################
    #     Mathematical | advanced arithmetical operations     #
    ###########################################################

    def permute_along_batch(self, permutation: Sequence[int] | Tensor) -> TBatchList:
        return self.__class__([self._data[i] for i in permutation])

    def permute_along_batch_(self, permutation: Sequence[int] | torch.Tensor) -> None:
        self._data = [self._data[i] for i in permutation]

    ################################################
    #     Mathematical | point-wise operations     #
    ################################################

    ###########################################
    #     Mathematical | trigo operations     #
    ###########################################

    ##########################################################
    #    Indexing, slicing, joining, mutating operations     #
    ##########################################################

    def append(self, other: BatchList | Sequence[T]) -> None:
        if isinstance(other, BatchList):
            other = other.data
        self._data.extend(other)

    def chunk_along_batch(self, chunks: int) -> tuple[TBatchList, ...]:
        if chunks < 1:
            raise RuntimeError(f"chunks has to be greater than 0 but received {chunks}")
        return self.split_along_batch(math.ceil(self.batch_size / chunks))

    def extend(self, other: Iterable[BatchList | Sequence[T]]) -> None:
        for batch in other:
            self.append(batch)

    def index_select_along_batch(self, index: Tensor | Sequence[int]) -> TBatchList:
        return self.__class__([self._data[i] for i in index])

    def select_along_batch(self, index: int) -> T:
        return self._data[index]

    def slice_along_batch(
        self, start: int = 0, stop: int | None = None, step: int = 1
    ) -> TBatchList:
        return self.__class__(self._data[start:stop:step])

    def split_along_batch(
        self, split_size_or_sections: int | Sequence[int]
    ) -> tuple[TBatchList, ...]:
        if isinstance(split_size_or_sections, int):
            return tuple(
                self.__class__(self._data[i : i + split_size_or_sections])
                for i in range(0, self.batch_size, split_size_or_sections)
            )
        i = 0
        output = []
        for size in split_size_or_sections:
            output.append(self.__class__(self._data[i : i + size]))
            i += size
        return tuple(output)

    ########################
    #     mini-batches     #
    ########################
