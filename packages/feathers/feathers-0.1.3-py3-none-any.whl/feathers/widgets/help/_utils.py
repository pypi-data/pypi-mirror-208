from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


def arrange_items_in_columns(items: list[T], rows: int, cols: int) -> list[tuple[T, ...]]:
    """
    Distribute items from a list into a table-like structure with the specified number of rows and columns.

    Items are assigned to columns first, then to rows. The output is a list of tuples, where each
    inner tuple represents a row in the table-like structure.

    Args:
        items (list): The input list of items to distribute.
        rows (int): The number of rows in the resulting table-like structure.
        cols (int): The number of columns in the resulting table-like structure.

    Returns:
        List[tuple[T]]: A list of tuples, where each inner list represents a row in the table-like structure.

    Example:
        >>> items = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        >>> rows = 5
        >>> cols = 3
        >>> distribute_items_in_columns(items, rows, cols)
        [['a', 'f'], ['b', 'g'], ['c'], ['d'], ['e']]
    """
    result = []
    for i in range(rows):
        row_items = []
        for j in range(cols):
            index = i + j * rows
            if index < len(items):
                row_items.append(items[index])
        result.append(tuple(row_items))
    return result
