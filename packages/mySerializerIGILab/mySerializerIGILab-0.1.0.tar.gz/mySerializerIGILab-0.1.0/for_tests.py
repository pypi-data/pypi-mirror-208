import math
def func(val):
    return math.sin(val + 5)


def decorator(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        return res
    return wrapper


class A:
    field = 5

    def test1(self):
        return self.field - 5

    @staticmethod
    def static_test1():
        return A.field


class B:
    field = 7

    def test2(self):
        return self.field + 3


class C(A, B):
    pass
