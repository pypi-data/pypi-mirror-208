from bool_to_int8_ray import bool_to_int8_batch, int8_to_bool_batch
import numpy as np


def test_1():
    hashvalues = np.array([[1, 0, 1, 0, 1, 1, 0, 0]])
    serialized = bool_to_int8_batch(hashvalues)
    deserialized = int8_to_bool_batch(serialized)
    np.testing.assert_array_equal(deserialized, hashvalues)


def test_2():
    hashvalues = (np.random.normal(size=(10000, 1024)) > 0).astype(np.uint8)
    serialized = bool_to_int8_batch(hashvalues)
    deserialized = int8_to_bool_batch(serialized)
    np.testing.assert_array_equal(deserialized, hashvalues)
    assert deserialized.shape == (10000, 1024)
    assert serialized.shape == (10000, 128)
