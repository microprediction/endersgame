

def test_ewvar():
    """
    Test the EWVar class from river.stats to ensure it calculates the exponentially weighted variance correctly.
    """
    from river import stats
    import math

    # Initialize EWVar with a fading_factor corresponding to decay
    decay = 0.99
    fading_factor = 1 - decay  # fading_factor = 0.1
    ew_var = stats.EWVar(fading_factor=fading_factor)

    # Data points to update EWVar with
    data = [1, -1, 1, -1, 1,-1]*10

    # Alpha for manual calculation
    alpha = fading_factor

    mean = None
    var = 0.0

    for x in data:
        if mean is None:
            # First data point initialization
            mean = x
            var = 0.0
        else:
            delta = x - mean
            mean += alpha * delta
            var = (1 - alpha) * (var + alpha * delta ** 2)

        # Update the EWVar instance
        ew_var.update(x)

        # Retrieve the variance from EWVar
        ew_var_value = ew_var.get()

        # Compare the calculated variance with the expected variance
        assert math.isclose(ew_var_value, var, rel_tol=1e-6), (
            f"At x={x}, expected var={var}, got {ew_var_value}"
        )

    print("EWVar test passed.")
