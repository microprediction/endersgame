from endersgame.riverstats.fewmean import FEWMean


def finite_ewa(xs, fading_factor=0.1):
    # Weight most recent samples more
    x_sum = 0
    weight_sum = 0
    weight = 1.0

    for x in reversed(xs):
        x_sum += weight * x
        weight_sum += weight
        weight *= (1-fading_factor)

    return x_sum / weight_sum


def test_fewmean():
    xs = [1, 2, 3, 4, 5]
    fading_factor = 0.1

    # Get result from finite sample correct EWA function
    f_ewa = finite_ewa(xs, fading_factor=fading_factor)
    print(f"Finite Sample EWA: {f_ewa:.5f}")

    # Get result from FEWMean class
    ewa_calc = FEWMean(fading_factor=fading_factor)
    for x in xs:
        ewa_calc.update(x)
    class_ewa = ewa_calc.get()
    print(f"FEWMean Class EWA: {class_ewa:.5f}")

    # Assert the results are close within a tolerance
    assert abs(f_ewa - class_ewa) < 1e-5, f"Mismatch in EWA: {f_ewa} != {class_ewa}"

    print("Test passed! The finite sample and FEWMean results match.")


if __name__ == '__main__':
    test_fewmean()
