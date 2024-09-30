from endersgame.riveralternatives.fewvar import FEWVar


def finite_ewvar(xs, fading_factor=0.1):
    # Initialize variables to calculate EWA and EWVar
    x_sum = 0
    x_square_sum = 0
    weight_sum = 0
    weight = 1.0

    # Calculate weighted mean and variance
    for x in reversed(xs):
        x_sum += weight * x
        x_square_sum += weight * x ** 2
        weight_sum += weight
        weight *= fading_factor

    # Calculate the weighted mean
    mean = x_sum / weight_sum

    # Calculate the weighted variance
    variance = (x_square_sum / weight_sum) - mean ** 2

    return mean, variance


def test_fewvar():
    xs = [1, 2, 3, 4, 5]
    fading_factor = 0.1

    # Get the finite sample mean and variance
    finite_mean, finite_variance = finite_ewvar(xs, fading_factor=fading_factor)
    print(f"Finite Sample - Mean: {finite_mean:.5f}, Variance: {finite_variance:.5f}")

    # Get the mean and variance from FEWVar
    ewvar_calc = FEWVar(fading_factor=fading_factor)
    for x in xs:
        ewvar_calc.update(x)

    ew_mean = ewvar_calc.get_mean()
    ew_variance = ewvar_calc.get()

    print(f"FEWVar - Mean: {ew_mean:.5f}, Variance: {ew_variance:.5f}")

    # Assertions to verify correctness
    assert abs(finite_mean - ew_mean) < 1e-5, f"Mean mismatch: {finite_mean} != {ew_mean}"
    assert abs(finite_variance - ew_variance) < 1e-5, f"Variance mismatch: {finite_variance} != {ew_variance}"

    print("Test passed! The finite sample and FEWVar results match.")


if __name__ == '__main__':
    test_fewvar()
