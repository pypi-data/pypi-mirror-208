PRIMITIVES = [10, 1.34, "string", "[1 , 2, 3, 5]", [1, 2, 3], {1: {1: {1: {1: {1: 1}}}}}, None, True, False,
              1 + 5j, {1, 2, 3, 4}, (1, 4), frozenset({1, 2}), [], bytes([48, 49, 50]), bytearray([51, 52, 53])]

class t:
    @staticmethod
    def lol():
        return "lol"

    @classmethod
    def clsmet(cls):
        return cls._LOL

    def f(self):
        return 1

    _LOL = 1 - 0


class T(t):
    _X = 11

    A = 10
    B = 11
    C = 14

    @staticmethod
    def tst4():
        return 123 * T._X

    def __init__(self):
        self.xy = 10

    def inf(self):
        print(self.xy, " ", self._LOL)


def rec_func(a):
    return rec_func(a - 1) + 1 if a > 1 else 1


def my_decorator(func):
    def cwrapper(*args, **kwargs):
        return 10 * func(*args, **kwargs)

    return cwrapper


def for_dec(a):
    return 2 * a


decorated_func = my_decorator(for_dec)


def gen():
    for i in range(10):
        yield i

