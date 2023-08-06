from __future__ import annotations

from typing import Generic, Iterable, Callable, SupportsIndex, TypeVar

from srtlst.sorted_list import SortedList
from srtlst.protocols import _SupportsLT

_T = TypeVar("_T")
_S = TypeVar("_S", bound=_SupportsLT)


class SortedListByKey(SortedList[_T], Generic[_T]):  # type:ignore[type-var]
    """
    a list that stays sorted under all operations using a key function
    """

    def __init__(self, seq: Iterable[_T] = (), /, *, key: Callable[[_T], _S]):
        """
        create a new sorted list from an optional iterable of values,
        with a key function to map items in the list to values to sort by
        """
        self._list = list(sorted(seq, key=key))
        self._key = key

    def __getitem__(
        self, index: SupportsIndex | slice
    ) -> SortedListByKey[_T] | _T:  # type:ignore[override]
        """
        return the value at position index,
        or, if index is a slice, return a SortedListByKey
        """
        found = self._list[index]
        if isinstance(found, list):
            return SortedListByKey(found, key=self._key)
        else:
            return found

    def __copy__(self) -> SortedListByKey[_T]:
        """
        return a shallow copy of the sorted list by key
        """
        return SortedListByKey(self._list, key=self._key)
