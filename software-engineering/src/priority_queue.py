"""Generic Priority Queue"""

from typing import TypeVar, Generic, List, Callable, Protocol
from abc import abstractmethod

T = TypeVar("T")

class Comparable(Protocol):
    """Abstract Comparable Types"""

    @abstractmethod
    def __lt__(self: T, other: T, /) -> bool:
        pass

CT = TypeVar("CT", bound=Comparable)

class PriorityQueue(Generic[CT]):
    """Generic Priority Queue"""

    def __init__(self, comparator: Callable[[CT, CT], bool] = lambda a, b: a < b):
        self._size: int = 0
        self._heap: List[CT] = []
        self._comparator = comparator

    def __len__(self):
        return self._size

    def __bool__(self):
        return self._size != 0

    def _float_up(self, item_index: int):
        if item_index == 0:
            return
        parent = (item_index - 1) // 2
        if not self._comparator(self._heap[parent], self._heap[item_index]):
            self._heap[parent], self._heap[item_index] = (
                self._heap[item_index],
                self._heap[parent],
            )
            self._float_up(parent)

    def _sink_down(self, item_index: int):
        left_child = 2 * item_index + 1
        right_child = 2 * item_index + 1
        smaller_child = self._smaller_child(left_child, right_child)
        if smaller_child is None:
            return
        if not self._comparator(self._heap[item_index], self._heap[smaller_child]):
            self._heap[item_index], self._heap[smaller_child] = (
                self._heap[smaller_child],
                self._heap[item_index],
            )
            self._sink_down(smaller_child)

    def _smaller_child(self, left: int, right: int) -> int | None:
        if left > self._size - 1:  # No child
            return None
        if left == self._size - 1:  # only left child
            return left
        return left if self._comparator(self._heap[left], self._heap[right]) else right

    def push(self, item: CT):
        """Add an item to the priority queue

        Args:
            item (T): The item to be added
        """
        self._heap.append(item)
        self._size += 1
        self._float_up(self._size - 1)

    def top(self) -> CT:
        """Returns the smallest item in the priority queue

        Raises:
            IndexError: Raised if the PQ is empty

        Returns:
            T: The smallest item
        """
        if self._size == 0:
            raise IndexError("read an empty priority queue")
        return self._heap[0]

    def pop(self) -> CT:
        """Remove and return the smallest item

        Raises:
            IndexError: Raised if the PQ is empty

        Returns:
            T: The removed item, which was the smallest in the PQ
        """
        if self._size == 0:
            raise IndexError("pop from empty priority queue")
        top = self._heap[0]
        self._heap[0] = self._heap[self._size - 1]
        self._heap.pop()
        self._size -= 1
        self._sink_down(0)
        return top
