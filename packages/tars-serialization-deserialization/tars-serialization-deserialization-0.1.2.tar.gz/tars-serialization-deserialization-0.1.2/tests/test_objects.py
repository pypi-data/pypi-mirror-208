import math

import pytest

test_list = [1, "qwe", 3, 22.8, (1, 2, 3), False, None]


@pytest.mark.skip
def test_mul(n):
    return n * 2


@pytest.mark.skip
def test_fact(n):
    if n == 0:
        return 1
    else:
        return n * test_fact(n - 1)


def func_with_builtin_func(arr: list):
    res = sorted(arr)

    return res


@pytest.mark.skip
def test_wrapper(n):
    return test_fact(n - 1) * n


@pytest.mark.skip
def test_vars(n):
    return test_list, n


class Person:
    religion = "aboba"

    def __init__(self, age=3):
        self.age = age

    def get_age(self):
        return self.age


class VeyComplicatedClass:
    country = "Moscow"

    def __init__(self, person_number=3):
        self.persons = []
        for i in range(person_number):
            self.persons.append(Person(i))

    def get_some_useless_info(self):
        result = 0
        for person in self.persons:
            result += person.age

        return result


test_dict_func = {test_wrapper: test_fact}

c = 42


def butoma(x, y):
    return math.sin(x * y * c)
