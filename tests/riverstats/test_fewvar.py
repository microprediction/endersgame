
from endersgame.riverstats.fewvar import FEWVar


def finite_sample_fewvar(xs, fading_factor=0.1):
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
        weight *= (1-fading_factor)

    # Calculate the weighted mean
    mean = x_sum / weight_sum

    # Calculate the weighted variance
    variance = (x_square_sum / weight_sum) - mean**2

    return mean, variance


def test_fewvar():
    xs = [1, 2, 3, 4, 5]
    fading_factor = 0.01
    mean, variance = finite_sample_fewvar(xs, fading_factor=fading_factor)
    print("Corrected Exponentially Weighted Mean:", mean)
    print("Corrected Exponentially Weighted Variance:", variance)

    ewvar_calc = FEWVar(fading_factor=fading_factor)
    for x in xs:
        ewvar_calc.update(x)
    print("Exponentially Weighted Mean:", ewvar_calc.get_mean())
    print("Exponentially Weighted Variance:", ewvar_calc.get())

