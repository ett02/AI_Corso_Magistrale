from collections import deque
import heapq

FIFOQueue = deque # alias for FIFO queue, used in Breadth-First Search

LIFOQueue = list # alias for LIFO queue, used in Depth-First Search

class PriorityQueue:
    """A queue in which the item with minimum f(item) is always popped first."""

    def __init__(self, items=(), key=lambda x: x):
        self.key = key # lambda function that returns the priority of an item
        self.items = [] # a heap of (score, item) pairs (the heap is a data structure that allows efficient retrieval of the minimum element)
        for item in items:
            self.add(item)

    def add(self, item):
        """Add item to the queue."""
        pair = (self.key(item), item)
        heapq.heappush(self.items, pair) # the heappush function maintains the heap property

    def pop(self):
        """Pop and return the item with min f(item) value."""
        return heapq.heappop(self.items)[1] # the heappop function removes and returns the smallest item from the heap
        # the [1] is used to return the item itself, not the pair (score, item)

    def top(self): return self.items[0][1] # the top function returns the smallest item from the heap without removing it

    def __len__(self): return len(self.items)