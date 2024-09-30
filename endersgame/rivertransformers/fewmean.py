
class FEWMean:

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
            weight = self.fading_factor * self.weight_sum
            self.ewa = (weight * self.ewa + x) / (weight + 1)
            self.weight_sum = weight + 1

    def get(self):
        # Return the current EWA
        return self.ewa



def correct_ewa(xs, fading_factor=0.1):
    # Weight most recent samples more
    x_sum = 0
    weight_sum = 0
    weight = 1.0

    for x in reversed(xs):
        x_sum += weight*x
        weight_sum += weight
        weight *= fading_factor

    return x_sum/weight_sum


if __name__=='__main__':

    # Example usage
    xs = [1, 2, 3, 4, 5]
    fading_factor = 0.1
    result_1 = correct_ewa(xs, fading_factor=fading_factor)
    ewa_calc = FEWMean(fading_factor=fading_factor)
    for x in xs:
        ewa_calc.update(x)
    result_2 = ewa_calc.get()

    # Sample usage
    print({'result1':result_1,'result2':result_2})


