from endersgame.attackers.baseattacker import BaseAttacker


class MomentumAttacker(BaseAttacker):

    # This will receive one value at a time
    # If it thinks that the values will be higher than the current one in the future, it returns a positive number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffer = []

    def __call__(self,x:float)->float:
        self._buffer.append(x)
        if len(self._buffer)<10:
            






