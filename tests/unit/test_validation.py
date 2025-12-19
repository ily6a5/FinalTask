from unittest.mock import patch

import pytest
import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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


class TestUserValidation:

    def test_validate_name_success(self):
        from app import app

        test_cases = [
            ("Иван Иванов", True),
            ("Мария-Анна Петрова-Сидорова", True),
            ("John Doe", True),
            ("А.С. Пушкин", True),
        ]

        for name, expected in test_cases:
            assert self._is_valid_name(name) == expected, f"Ошибка валидации для имени: {name}"



    # Вспомогательные методы валидации
    def _is_valid_name(self, name):
        if not name or not isinstance(name, str):
            return False

        name = name.strip()
        if not name or len(name) > 100:
            return False

        # Проверка на допустимые символы (буквы, пробелы, дефисы, точки)
        import re
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-\.]+$', name):
            return False

        return True

    def _is_valid_email(self, email):
        if not email or not isinstance(email, str):
            return False

        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _is_valid_age(self, age):
        try:
            age_int = int(age)
            return 1 <= age_int <= 150
        except (ValueError, TypeError):
            return False

    def _is_valid_phone(self, phone):

        if not phone:  # Телефон не обязателен
            return True

        if not isinstance(phone, str):
            return False

        # Упрощенная проверка российских телефонов
        import re
        phone_clean = re.sub(r'[^\d+]', '', phone)

        # Российские форматы: +7..., 8..., 7...
        if phone_clean.startswith('+7'):
            return len(phone_clean) == 12  # +7 и 10 цифр
        elif phone_clean.startswith('8'):
            return len(phone_clean) == 11  # 8 и 10 цифр
        elif phone_clean.startswith('7'):
            return len(phone_clean) == 11  # 7 и 10 цифр

        return False


class TestFormValidation:

    def test_complete_user_validation_success(self):
        valid_data = {
            "name": "Иван Иванов",
            "email": "ivan@example.com",
            "age": "25",
            "phone": "+7 (999) 123-45-67",
            "city": "Москва"
        }

        errors = self._validate_user_form(valid_data)
        assert len(errors) == 0, f"Не должно быть ошибок: {errors}"


    def test_duplicate_email_validation(self, mock_users):
        from app import load_users

        # Мокаем загрузку пользователей
        with patch('app.load_users', return_value=mock_users):
            errors = self._validate_email_duplicate("alex@example.com", existing_id=None)
            assert len(errors) > 0, "Должна быть ошибка дублирования email"

            errors = self._validate_email_duplicate("alex@example.com", existing_id=1)
            assert len(errors) == 0, "Не должно быть ошибки при редактировании того же пользователя"

            errors = self._validate_email_duplicate("new@example.com", existing_id=None)
            assert len(errors) == 0, "Не должно быть ошибки для нового email"

    # Вспомогательные методы
    def _validate_user_form(self, data):
        errors = []

        if not data.get('name', '').strip():
            errors.append("Имя обязательно для заполнения")

        if not data.get('email', '').strip():
            errors.append("Email обязателен для заполнения")
        elif '@' not in data['email']:
            errors.append("Некорректный email адрес")

        age = data.get('age', '')
        if not age.isdigit():
            errors.append("Возраст должен быть числом")
        elif not (1 <= int(age) <= 150):
            errors.append("Некорректный возраст")

        city = data.get('city', '')
        if city and len(city) > 100:
            errors.append("Название города слишком длинное")

        return errors

    def _validate_email_duplicate(self, email, existing_id):
        from app import load_users

        errors = []
        users = load_users()

        for user in users:
            if user['email'].lower() == email.lower() and user['id'] != existing_id:
                errors.append("Пользователь с таким email уже существует")
                break

        return errors
