
import pytest

@pytest.fixture
def mock_users():
    return [
        {
            "id": 1,
            "name": "Александр Петров",
            "email": "alex@example.com",
            "age": 28,
            "phone": "+7 (911) 111-11-11",
            "city": "Москва"
        },
        {
            "id": 2,
            "name": "Мария Иванова",
            "email": "maria@example.com",
            "age": 32,
            "phone": "+7 (922) 222-22-22",
            "city": "Казань"
        },
        {
            "id": 3,
            "name": "Иван Сидоров",
            "email": "ivan@example.com",
            "age": 45,
            "phone": "+7 (933) 333-33-33",
            "city": "Новосибирск"
        }
    ]



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
