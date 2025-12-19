
import pytest

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 3 - 1 == 2

class TestMathOperations:

    def test_multiplication(self):
        assert 2 * 3 == 6

    def test_division(self):
        assert 6 / 2 == 3

    def test_division_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            result = 1 / 0
