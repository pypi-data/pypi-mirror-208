import builtins


def calc_precision(value: float, precision: int = 2):
    real_precision = precision
    abs_value = abs(value)
    while 0 < abs_value < 1/pow(10, real_precision):
        real_precision += precision

    return real_precision


def round(value: float, precision: int = 2):
    return builtins.round(value, calc_precision(value, precision))
