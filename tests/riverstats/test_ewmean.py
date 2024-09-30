
import math
import pytest
from river import stats

def test_ewmean():
    """
    Test the EWMean class from river.stats to ensure it calculates the exponentially weighted average correctly.
    """
    # Define a sequence of data points
    data_points = [1, 2, 3, 4, 5]

    # Define a fading factor
    fading_factor = 0.5  # You can adjust this value to test different scenarios

    # Initialize EWMean with the specified fading factor
    ew_mean = stats.EWMean(fading_factor=fading_factor)

    # List to store expected EWA values
    expected_ewas = []

    # Variable to keep track of the manually computed EWA
    manual_ewa = None
    alpha = fading_factor

    for idx, x in enumerate(data_points):
        # Update EWMean instance
        ew_mean.update(x)
        computed_ewa = ew_mean.get()

        # Manually compute EWA
        if manual_ewa is None:
            manual_ewa = x  # Initialization step
        else:
            manual_ewa = alpha * x + (1 - alpha) * manual_ewa

        expected_ewas.append(manual_ewa)

        # Assert that the computed EWA matches the manual calculation within a tolerance
        assert math.isclose(computed_ewa, manual_ewa, rel_tol=1e-9), (
            f"At index {idx}, expected EWA={manual_ewa}, got {computed_ewa}"
        )

    # Optional: Print success message
    print("EWMean test passed for fading_factor=0.5 with data_points=[1,2,3,4,5].")

def test_ewmean_edge_cases():
    """
    Test the EWMean class for edge cases such as constant data points and extreme fading factors.
    """
    # Test Case 1: Constant Data Points
    data_points = [5, 5, 5, 5, 5]
    fading_factor = 0.3
    ew_mean = stats.EWMean(fading_factor=fading_factor)
    manual_ewa = None

    for x in data_points:
        ew_mean.update(x)
        computed_ewa = ew_mean.get()

        if manual_ewa is None:
            manual_ewa = x
        else:
            manual_ewa = fading_factor * x + (1 - fading_factor) * manual_ewa

        assert math.isclose(computed_ewa, manual_ewa, rel_tol=1e-9), (
            f"Constant Data Points: Expected EWA={manual_ewa}, got {computed_ewa}"
        )

    print("EWMean edge case test passed for constant data points.")

    # Test Case 2: High Fading Factor (alpha=1.0)
    data_points = [10, 20, 30]
    fading_factor = 1.0
    ew_mean = stats.EWMean(fading_factor=fading_factor)
    manual_ewa = None

    for x in data_points:
        ew_mean.update(x)
        computed_ewa = ew_mean.get()

        if manual_ewa is None:
            manual_ewa = x
        else:
            manual_ewa = fading_factor * x + (1 - fading_factor) * manual_ewa  # Should always be x

        assert math.isclose(computed_ewa, manual_ewa, rel_tol=1e-9), (
            f"High Fading Factor: Expected EWA={manual_ewa}, got {computed_ewa}"
        )

    print("EWMean edge case test passed for high fading_factor=1.0.")

    # Test Case 3: Low Fading Factor (alpha=0.0)
    data_points = [10, 20, 30]
    fading_factor = 0.0
    ew_mean = stats.EWMean(fading_factor=fading_factor)
    manual_ewa = None

    for x in data_points:
        ew_mean.update(x)
        computed_ewa = ew_mean.get()

        if manual_ewa is None:
            manual_ewa = x
        else:
            manual_ewa = fading_factor * x + (1 - fading_factor) * manual_ewa  # Should remain manual_ewa

        assert math.isclose(computed_ewa, manual_ewa, rel_tol=1e-9), (
            f"Low Fading Factor: Expected EWA={manual_ewa}, got {computed_ewa}"
        )

    print("EWMean edge case test passed for low fading_factor=0.0.")

def test_ewmean_initialization():
    """
    Test that EWMean initializes correctly with the first data point.
    """
    ew_mean = stats.EWMean(fading_factor=0.3)
    first_data_point = 10
    ew_mean.update(first_data_point)
    computed_ewa = ew_mean.get()
    expected_ewa = first_data_point

    assert math.isclose(computed_ewa, expected_ewa, rel_tol=1e-9), (
        f"Initialization: Expected EWA={expected_ewa}, got {computed_ewa}"
    )

    print("EWMean initialization test passed.")

def test_ewmean_negative_data():
    """
    Test EWMean with negative data points.
    """
    data_points = [-1, -2, -3, -4, -5]
    fading_factor = 0.4
    ew_mean = stats.EWMean(fading_factor=fading_factor)
    manual_ewa = None

    for idx, x in enumerate(data_points):
        ew_mean.update(x)
        computed_ewa = ew_mean.get()

        if manual_ewa is None:
            manual_ewa = x
        else:
            manual_ewa = fading_factor * x + (1 - fading_factor) * manual_ewa

        assert math.isclose(computed_ewa, manual_ewa, rel_tol=1e-9), (
            f"Negative Data: At index {idx}, expected EWA={manual_ewa}, got {computed_ewa}"
        )

    print("EWMean negative data test passed.")
