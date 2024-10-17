from midone.riverstats.fewvar import FEWVar  # Adjust the import path to match your project structure


def test_fewvar_to_dict():
    # Initialize and update FEWVar
    few_var = FEWVar(fading_factor=0.01)
    few_var.update(5.0)
    few_var.update(6.0)

    # Serialize to dictionary
    state = few_var.to_dict()

    # Assert the serialized dictionary contains the correct state
    assert state == {
        'fading_factor': 0.01,
        'ewa': few_var.get_mean(),
        'ewv': few_var.get(),
        'weight_sum': few_var.weight_sum
    }

def test_fewvar_from_dict():
    # Define the serialized state
    state = {
        'fading_factor': 0.01,
        'ewa': 5.5,
        'ewv': 0.25,
        'weight_sum': 2
    }

    # Deserialize into FEWVar
    restored_few_var = FEWVar.from_dict(state)

    # Assert the restored object matches the expected state
    assert restored_few_var.fading_factor == 0.01
    assert restored_few_var.get_mean() == 5.5
    assert restored_few_var.get() == 0.25
    assert restored_few_var.weight_sum == 2
