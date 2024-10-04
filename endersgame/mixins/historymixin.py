from collections import deque
from endersgame.gameconfig import DEFAULT_HISTORY_LEN


class HistoryMixin:
    """
    A mixin that provides history management functionality with a fixed-length buffer.
    Classes that require history tracking can inherit from this mixin to manage
    a deque-based history.
    """

    def __init__(self, max_history_len=DEFAULT_HISTORY_LEN):
        self.max_history_len = max_history_len  # Store as an instance attribute
        self.history = deque(maxlen=max_history_len)  # Fixed-length buffer for history

    def tick_history(self, x) -> None:
        """
        Adds a value `x` to the history deque. Automatically removes the oldest value
        if the max length is reached. Coerces `x` to float.

        Parameters:
        - x: The value to add to history. Will be coerced to float.
        """
        try:
            x = float(x)
        except (ValueError, TypeError):
            x = 0.0  # Default value if conversion fails
        self.history.append(x)

    def get_recent_history(self, n: int=None) -> list:
        """
        Returns the `n` most recent values from the history.
        If there are fewer than `n` values in the history, returns as many as available.

        Parameters:
        - n (int): Number of recent history elements to retrieve.

        Returns:
        - list: A list of the most recent `n` history values.
        """
        if n is None:
            return list(self.history)
        else:
            return list(self.history)[-n:]

    def __len__(self):
        return len(self.history)

    def is_history_full(self) -> bool:
        """
        Checks if the history buffer is full.

        Returns:
        - bool: True if history is full, False otherwise.
        """
        return len(self.history) == self.history.maxlen

    def to_dict(self) -> dict:
        """
        Serializes the state of the HistoryMixin object to a dictionary.

        Returns:
        - dict: A dictionary containing the serialized state.
        """
        return {
            'max_history_len': self.max_history_len,
            'history': list(self.history)  # Convert deque to list for serialization
        }

    @classmethod
    def from_dict(cls, state: dict):
        """
        Deserializes the state from a dictionary into a new HistoryMixin instance.

        Parameters:
        - data (dict): A dictionary containing the serialized state.

        Returns:
        - HistoryMixin: A new instance of HistoryMixin with the restored state.
        """
        max_history_len_with_fallback = state.get('max_history_len', DEFAULT_HISTORY_LEN)
        instance = cls(max_history_len=max_history_len_with_fallback)
        history_data = state.get('history', [])
        instance.history = HistoryMixin.set_history(history_data=history_data, maxlen=max_history_len_with_fallback)
        return instance

    @staticmethod
    def set_history(history_data, maxlen):
        coerced_history = []
        for item in history_data:
            try:
                coerced_item = float(item)
            except (ValueError, TypeError):
                coerced_item = 0.0  # Default value if conversion fails
            coerced_history.append(coerced_item)
        history = deque(coerced_history, maxlen=maxlen)
        return history

