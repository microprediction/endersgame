from river import stats

class FEWMean(stats.base.Univariate):

    def __init__(self, fading_factor=0.01):
        # Initialize the fading factor and state variables
        self.fading_factor = fading_factor
        self.ewa = None
        self.weight_sum = 0

    def update(self, x):
        # If this is the first data point, set ewa to x
        if self.ewa is None:
            self.ewa = x
            self.weight_sum = 1
        else:
            # Incrementally update the EWA using the fading factor
            weight = (1 - self.fading_factor) * self.weight_sum
            self.ewa = (weight * self.ewa + x) / (weight + 1)
            self.weight_sum = weight + 1

    def tick(self, x):
        return self.update(x)

    def get(self):
        # Return the current EWA
        return self.ewa if self.ewa is not None else 0

    def to_dict(self):
        """
        Serializes the state of the FEWMean object to a dictionary.
        """
        return {
            'fading_factor': self.fading_factor,
            'ewa': self.ewa,
            'weight_sum': self.weight_sum
        }

    @classmethod
    def from_dict(cls, data):
        """
        Deserializes the state from a dictionary into a new FEWMean instance.
        """
        instance = cls(fading_factor=data['fading_factor'])
        instance.ewa = data['ewa']
        instance.weight_sum = data['weight_sum']
        return instance
