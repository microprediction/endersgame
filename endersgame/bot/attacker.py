UP = 1.
DOWN = -1.
SAME = 0.

import random

class RandomAttacker:
    def tick_and_predict(self, y: float, k:int=None)->float:
        return random.choice([UP, DOWN, SAME])

class UpAttacker:
    def tick_and_predict(self, y: float, k:int=None)->float:
        return UP
