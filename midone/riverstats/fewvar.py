from river import stats

class FEWVar(stats.base.Univariate):

    def __init__(self, fading_factor=0.01):
        # Initialize the fading factor and state variables
        self.fading_factor = fading_factor
        self.ewa = None  # Exponentially weighted average (mean)
        self.ewv = None  # Exponentially weighted variance
        self.weight_sum = 0

    def update(self, x):
        # If this is the first data point, set ewa to x and initialize variance
        if self.ewa is None:
            self.ewa = x
            self.ewv = 0  # Variance starts at 0 with one sample
            self.weight_sum = 1
        else:
            # Incrementally update the EWA (mean)
            weight = (1-self.fading_factor) * self.weight_sum
            previous_ewa = self.ewa
            self.ewa = (weight * self.ewa + x) / (weight + 1)
            self.weight_sum = weight + 1

            # Update the EW variance
            deviation = x - previous_ewa
            self.ewv = (weight * self.ewv + deviation * (x - self.ewa)) / (weight + 1)

    def tick(self, x):
        return self.update(x=x)

    def get(self):
        # Return the current exponentially weighted variance
        return self.ewv if self.ewv is not None else 0

    def get_mean(self):
        # Return the current exponentially weighted mean (for reference)
        return self.ewa if self.ewa is not None else 0

    def to_dict(self):
        """
        Serializes the state of the FEWVar object to a dictionary.
        """
        return {
            'fading_factor': self.fading_factor,
            'ewa': self.ewa,
            'ewv': self.ewv,
            'weight_sum': self.weight_sum
        }

    @classmethod
    def from_dict(cls, data):
        """
        Deserializes the state from a dictionary into a new FEWVar instance.
        """
        instance = cls(fading_factor=data['fading_factor'])
        instance.ewa = data['ewa']
        instance.ewv = data['ewv']
        instance.weight_sum = data['weight_sum']
        return instance
