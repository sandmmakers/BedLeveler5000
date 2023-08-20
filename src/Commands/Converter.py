def floatToStr(value, *, prefix=None):
    string = f'{value}'
    return string if prefix is None else prefix + string