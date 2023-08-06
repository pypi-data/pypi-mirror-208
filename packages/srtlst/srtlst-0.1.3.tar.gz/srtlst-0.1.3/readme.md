# srtlst

_a simple, generically type-annotated, sorted list_

![python_version](https://img.shields.io/pypi/pyversions/srtlst)
[![mypy_checked](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

### usage

Create a sorted list like this:

```python
>>> from srtlst import SortedList
>>> s = SortedList([5, 3, 1])
>>> print(s)
[1, 3, 5]
```

A `SortedList` mimics a regular `list` in most ways, but remains sorted:

```python
>>> s = SortedList([5, 3, 1])
>>> s.extend([6, 2, 4])
>>> print(s)
[1, 2, 3, 4, 5, 6]
```

You can use `add()` instead of `insert()` or `append()`:

```python
>>> s = SortedList([5, 3, 1])
>>> s.add(3)
>>> s.add(2)
>>> print(s)
[1, 2, 3, 3, 5]
```

If your data is not inherently sortable, or you want to sort it in a non-default way, you can use `SortedListByKey`
and supply a function to sort it (just like with `sorted()`):

```python
>>> from srtlst import SortedListByKey
>>> my_function = lambda x: x * (-1) ** x
>>> s = SortedListByKey([1, 2, 3, 4], key=my_function)
>>> print(s)
[3, 1, 2, 4]
```

`SortedListByKey` behaves like a `SortedList` in all other ways, and indeed inherits from it.
However, when type checking, a `SortedList` only accepts values for which a less-than (`<`) method is defined (`__lt__()`).

`SortedListByKey` accepts any type of object, as long as an appropriate key function is provided.
The key function must return comparable values for the items in the list.

### installation

No surprises here:

```shell
$ pip install srtlst
```

### type checking

`SortedList` and `SortedListByKey` are type-hinted according to [PEP 484](https://peps.python.org/pep-0484/)
and the `srtlst` library is itself checked using `mypy --strict`.

Type hints for both containers can be provided using type arguments, just like with `list` and other containers:

```python
s: SortedList[int] = SortedList([3, 2, 1])
```

### performance

This library aims to provide a simple sorted list without any dependencies which is ready for use.
Some of the list operations are reimplemented to take advantage of the list's sortedness using Python's standard `bisect` library.

This library should suit your needs if you just want to keep stuff sorted, without having to implement the bookkeeping yourself.
However, if your sorting needs arise from the need for performance, you should also consider this library:
[sortedcontainers](https://grantjenks.com/docs/sortedcontainers/).  

### documentation

Documentation is work in progress. For now the Python's built-in help function can be of service:

```python
>>> from srtlst import SortedList
>>> help(SortedList)
```
