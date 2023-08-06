import numpy as np


def get_as_array(source):
    return source if isinstance(source, np.ndarray) else np.full(2, source, dtype=int)


def crossover(source1, source2):
    """
    The `source1`-series is defined as having crossed over `source2`-series if, on the current
    bar, the value of `source1` is greater than the value of `source2`, and on the previous
    bar, the value of `source1` was less than or equal to the value of `source2`.
    """
    source1 = get_as_array(source1)
    source2 = get_as_array(source2)
    return source1[0] > source2[0] and source1[1] < source2[1]


def crossunder(source1, source2):
    source1 = get_as_array(source1)
    source2 = get_as_array(source2)
    return source1[0] < source2[0] and source1[1] > source2[1]


def na(value):
    return value is None
