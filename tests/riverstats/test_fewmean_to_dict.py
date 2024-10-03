from endersgame.riverstats.fewmean import FEWMean  # Adjust the import path to match your project structure


def test_fewmean_to_dict():
    # Initialize and update FEWMean
    few_mean = FEWMean(fading_factor=0.01)
    few_mean.update(5.0)
    few_mean.update(6.0)

    # Serialize to dictionary
    state = few_mean.to_dict()

    # Assert the serialized dictionary contains the correct state
    assert state == {
        'fading_factor': 0.01,
        'ewa': few_mean.get(),
        'weight_sum': few_mean.weight_sum
    }

def test_fewmean_from_dict():
    # Define the serialized state
    state = {
        'fading_factor': 0.01,
        'ewa': 5.5,
        'weight_sum': 2
    }

    # Deserialize into FEWMean
    restored_few_mean = FEWMean.from_dict(state)

    # Assert the restored object matches the expected state
    assert restored_few_mean.fading_factor == 0.01
    assert restored_few_mean.get() == 5.5
    assert restored_few_mean.weight_sum == 2
