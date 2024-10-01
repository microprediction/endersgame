from collections import deque
import numpy as np


class HistoryMixin:
    """
    A mixin that provides history management functionality with a fixed-length buffer.
    Classes that require history tracking can inherit from this mixin to manage
    a deque-based history.
    """

    def __init__(self, max_history_len=200):
        self.history = deque(maxlen=max_history_len)  # Fixed-length buffer for history

    def tick_history(self, x: float) -> None:
        """
        Adds a value `x` to the history deque. Automatically removes the oldest value
        if the max length is reached.
        """
        self.history.append(x)

    def get_recent_history(self, n: int) -> np.ndarray:
        """
        Returns the `n` most recent values from the history.
        If there are fewer than `n` values in the history, returns as many as available.
        """
        return np.array(self.history)[-n:]

    def __len__(self):
        return len(self.history)

    def is_history_full(self) -> bool:
        """
        Checks if the history buffer is full.
        """
        return len(self.history) == self.history.maxlen
