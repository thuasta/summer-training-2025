"""Contains Tests for Priority Queue"""
import unittest
from src.priority_queue import PriorityQueue

class TestStringMethods(unittest.TestCase):
    """Test the priority queue"""

    def test_only_one_item_should_return_the_item(self):
        """Tests if PQ behaves well when there is only one element."""
        priority_queue: PriorityQueue[int] = PriorityQueue()
        priority_queue.push(1)

        self.assertEqual(1, priority_queue.top())

    def test_two_elements_pick_smaller(self):
        """"""
        priority_queue: PriorityQueue[int] = PriorityQueue()
        priority_queue.push(2)

        self.assertEqual(2, priority_queue.top())

        priority_queue.push(1)

        self.assertEqual(1, priority_queue.top())

    def test_empty_PQ_should_raise(self):
        priority_queue: PriorityQueue[int] = PriorityQueue()

        with self.assertRaises(IndexError):
            priority_queue.pop()
