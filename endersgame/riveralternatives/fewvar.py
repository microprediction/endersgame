

class FEWVar:

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
            weight = self.fading_factor * self.weight_sum
            previous_ewa = self.ewa
            self.ewa = (weight * self.ewa + x) / (weight + 1)
            self.weight_sum = weight + 1

            # Update the EW variance
            deviation = x - previous_ewa
            self.ewv = (weight * self.ewv + deviation * (x - self.ewa)) / (weight + 1)

    def get(self):
        # Return the current exponentially weighted variance
        return self.ewv

    def get_mean(self):
        # Return the current exponentially weighted mean (for reference)
        return self.ewa


def finite_sample_ewvar(xs, fading_factor=0.1):
    # Initialize variables to calculate EWA and EWVar
    x_sum = 0
    x_square_sum = 0
    weight_sum = 0
    weight = 1.0

    # Calculate weighted mean and variance
    for x in reversed(xs):
        x_sum += weight * x
        x_square_sum += weight * x**2
        weight_sum += weight
        weight *= fading_factor

    # Calculate the weighted mean
    mean = x_sum / weight_sum

    # Calculate the weighted variance
    variance = (x_square_sum / weight_sum) - mean**2

    return mean, variance


if __name__ == '__main__':
    xs = [1, 2, 3, 4, 5]
    fading_factor = 0.1
    mean, variance = finite_sample_ewvar(xs, fading_factor=fading_factor)
    print("Corrected Exponentially Weighted Mean:", mean)
    print("Corrected Exponentially Weighted Variance:", variance)

    ewvar_calc = FEWVar(fading_factor=fading_factor)
    for x in xs:
        ewvar_calc.update(x)
    print("Exponentially Weighted Mean:", ewvar_calc.get_mean())
    print("Exponentially Weighted Variance:", ewvar_calc.get())
