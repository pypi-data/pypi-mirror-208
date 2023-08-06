from __future__ import annotations
from bisect import insort_right, insort_left, bisect_right, bisect_left
from collections.abc import Iterable
from typing import TypeVar, Generic, Any, Iterator, SupportsIndex

from srtlst.protocols import _SupportsLT

_S = TypeVar("_S", bound=_SupportsLT)
_T = TypeVar("_T")


class SortedList(Generic[_S]):
    """
    a list that stays sorted under all operations
    """

    def __init__(self, seq: Iterable[_S] = (), /):
        """
        create a new sorted list from an optional iterable of values
        """
        self._key = lambda x: x
        self._list = list(sorted(seq, key=self._key))

    def add_right(self, value: _S) -> None:
        """
        add a value to the list and sort it into the right place
        (to the right of existing duplicate values,
        or of items with the same sort key value)
        """
        insort_right(self._list, value, key=self._key)

    def add_left(self, value: _S) -> None:
        """
        add a value to the list and sort it into the right place
        (to the left of existing duplicate values,
        or of items with the same sort key value)
        """
        insort_left(self._list, value, key=self._key)

    add = add_right

    def remove_right(self, value: _S) -> None:
        """
        remove a value from the list (if multiple exists, remove the right-most value)
        """
        position = bisect_right(self._list, value, key=self._key)
        value_key = self._key(value)
        for i in reversed(range(position)):
            if self._key(self._list[i]) != value_key:
                break
            if self._list[i] == value:
                del self._list[i]
                return
        raise ValueError(f"{value} not in list")

    def remove_left(self, value: _S) -> None:
        """
        remove a value from the list (if multiple exists, remove the left-most value)
        """
        position = bisect_left(self._list, value, key=self._key)
        value_key = self._key(value)
        for i in range(position, len(self._list)):
            if self._key(self._list[i]) != value_key:
                break
            if self._list[i] == value:
                del self._list[i]
                return
        raise ValueError(f"{value} not in list")

    remove = remove_right

    def pop_left(self) -> _S:
        """
        remove the left-most value from the list and return it
        """
        try:
            return self._list.pop(0)
        except IndexError:
            raise IndexError("pop from empty sorted list")

    def pop_right(self) -> _S:
        """
        remove the right-most value from the list and return it
        """
        try:
            return self._list.pop()
        except IndexError:
            raise IndexError("pop from empty sorted list")

    def pop(self, index: SupportsIndex | None = None, /) -> _S:
        """
        remove the right-most value from the list and return it,
        or, if an index is given, remove the value at index and return it
        """
        if index is not None:
            try:
                return self._list.pop(index)
            except IndexError:
                raise IndexError("pop from empty sorted list")
        else:
            try:
                return self._list.pop()
            except IndexError:
                raise IndexError("pop from empty sorted list")

    def extend(self, seq=Iterable[_S]):
        """
        add the values from an iterable to the list
        (to the right of pre-existing duplicates)
        """
        self._list.extend(seq)
        self._list.sort(key=self._key)

    def __copy__(self) -> SortedList[_S]:
        """
        return a shallow copy of the sorted list
        """
        return SortedList(self._list)

    def __str__(self) -> str:
        """
        return str(self)
        """
        return str(self._list)

    def __repr__(self) -> str:
        """
        return repr(self)
        """
        return repr(self._list)

    def __lt__(self, other: Any) -> bool:
        """
        return self < other
        """
        return self._list < other

    def __le__(self, other: Any) -> bool:
        """
        return self <= other
        """
        return self._list <= other

    def __eq__(self, other: Any) -> bool:
        """
        return self == other
        """
        return self._list == other

    def __ne__(self, other: Any) -> bool:
        """
        return self != other
        """
        return self._list != other

    def __gt__(self, other: Any) -> bool:
        """
        return self > other
        """
        return self._list > other

    def __ge__(self, other: Any) -> bool:
        """
        return self >= other
        """
        return self._list >= other

    def __iter__(self) -> Iterator[_S]:
        """
        return an iterator to the list
        """
        return iter(self._list)

    def __len__(self) -> int:
        """
        return the number of values in the list
        """
        return len(self._list)

    def __getitem__(self, index: SupportsIndex | slice) -> SortedList[_S] | _S:
        """
        return the value at position index,
        or, if index is a slice, return a SortedList
        """
        found = self._list[index]
        if isinstance(found, Iterable):
            return SortedList(found)
        else:
            return found

    def __delitem__(self, key: SupportsIndex | slice):
        """
        delete self[key]
        """
        del self._list[key]

    def __add__(self, other: list[_T]) -> list[_S | _T]:
        """
        return self + other as a list
        """
        return self._list + other

    def __mul__(self, other: SupportsIndex) -> list[_S]:
        """
        return self * other as a list
        """
        return self._list * other

    def __contains__(self, item: _S) -> bool:
        """
        return true if item in self, false otherwise
        """
        position = bisect_left(self._list, item, key=self._key)
        return position != len(self._list)

    def __iadd__(self, other: Iterable[_S]) -> SortedList[_S]:  # type:ignore[misc]
        """
        implement self += other
        """
        self._list += other
        self._list.sort(key=self._key)
        return self

    def __reversed__(self) -> Iterator[_S]:
        """
        return an iterator to the list in reversed order
        """
        # todo: return reverse SortedList, requires self._reverse
        return reversed(self._list)

    def clear(self):
        """
        remove all values from the list
        """
        self._list.clear()

    def index(self, x: _S, start: int | None = None, end: int | None = None) -> int:
        """
        return the position of the first occurrence of x in the list,
        if start and end are given only self[start:end] will be searched,
        or self[start:] or self[:end] if only one is given
        """
        lo = 0 if start is None else start
        hi = len(self._list) if end is None else end

        position = bisect_left(self._list, x, lo, hi, key=self._key)

        if position < hi and self._list[position] == x:
            return position
        else:
            raise ValueError(f"{x} is not in sorted list")

    def count(self, x: _S) -> int:
        """
        return the number of occurrences of x in the list
        """
        position = bisect_left(self._list, x, key=self._key)
        count = 0
        for item in self._list[position:]:
            if item == x:
                count += 1
            else:
                break
        return count
