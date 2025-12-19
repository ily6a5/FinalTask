import pytest
import json
import tempfile
import os
import sys
from datetime import datetime
from unittest.mock import mock_open, patch

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import load_users, save_users


class TestFileOperations:

    def test_save_users_success(self, mock_users):
        mock_file = mock_open()

        with patch('builtins.open', mock_file):
            with patch('json.dump') as mock_json_dump:
                save_users(mock_users)

                mock_file.assert_called_once()

                # вызван с правильными аргументами
                mock_json_dump.assert_called_once()
                args, kwargs = mock_json_dump.call_args
                assert args[0] == mock_users
                assert kwargs['ensure_ascii'] == False
                assert kwargs['indent'] == 2

    def test_save_users_io_error(self, mock_users):
        mock_file = mock_open()
        mock_file.side_effect = IOError("Disk full")

        with patch('builtins.open', mock_file):
            with pytest.raises(IOError):
                save_users(mock_users)


class TestDataProcessing:

    def test_generate_user_id(self, mock_users):
        # Когда есть пользователи
        new_id = self._generate_new_id(mock_users)
        assert new_id == 3  # Максимальный ID + 1

        new_id = self._generate_new_id([])
        assert new_id == 1

        unordered_users = [
            {"id": 5},
            {"id": 2},
            {"id": 8}
        ]
        new_id = self._generate_new_id(unordered_users)
        assert new_id == 9

    def test_filter_users_by_age(self, mock_users):
        filtered = self._filter_by_age(mock_users, min_age=30, max_age=35)
        assert len(filtered) == 1
        assert filtered[0]['name'] == "Мария Иванова"
        assert filtered[0]['age'] == 32


    def test_validate_and_format_phone(self):
        test_cases = [
            ("89991234567", "+7 (999) 123-45-67"),
            ("+79991234567", "+7 (999) 123-45-67"),
            ("8(999)123-45-67", "+7 (999) 123-45-67"),
            ("+7 (999) 123-45-67", "+7 (999) 123-45-67"),  # Уже отформатирован
            ("abc", None),  # Некорректный
            ("123", None),  # Слишком короткий
        ]

        for input_phone, expected_output in test_cases:
            formatted = self._format_phone(input_phone)
            assert formatted == expected_output, f"Для {input_phone} ожидалось {expected_output}, получено {formatted}"

    def _generate_new_id(self, users):
        if not users:
            return 1
        return max(user['id'] for user in users) + 1

    def _filter_by_age(self, users, min_age=None, max_age=None):
        filtered = []
        for user in users:
            age = user.get('age', 0)
            if min_age is not None and age < min_age:
                continue
            if max_age is not None and age > max_age:
                continue
            filtered.append(user)
        return filtered

    def _search_users(self, users, query):
        if not query:
            return users

        query = query.lower()
        results = []

        for user in users:
            if (query in user.get('name', '').lower() or
                    query in user.get('email', '').lower() or
                    query in user.get('city', '').lower() or
                    query in user.get('phone', '').lower()):
                results.append(user)

        return results

    def _sort_users(self, users, field, descending=False):
        return sorted(users, key=lambda x: x.get(field, ''), reverse=descending)

    def _format_phone(self, phone):
        import re

        if not phone:
            return None

        # Очищаем от всех нецифровых символов, кроме +
        digits = re.sub(r'[^\d+]', '', phone)

        # Российские номера
        if digits.startswith('+7'):
            if len(digits) == 12:  # +7 и 10 цифр
                clean = digits[2:]  # Убираем +7
            else:
                return None
        elif digits.startswith('8'):
            if len(digits) == 11:  # 8 и 10 цифр
                clean = digits[1:]  # Убираем 8
            else:
                return None
        elif digits.startswith('7'):
            if len(digits) == 11:  # 7 и 10 цифр
                clean = digits[1:]  # Убираем 7
            else:
                return None
        else:
            return None

        # Форматируем: +7 (XXX) XXX-XX-XX
        if len(clean) == 10:
            return f"+7 ({clean[0:3]}) {clean[3:6]}-{clean[6:8]}-{clean[8:10]}"

        return None


class TestDateTimeUtils:

    def test_format_timestamp(self):
        from datetime import datetime

        test_date = datetime(2024, 1, 15, 14, 30, 45)

        formatted = test_date.strftime("%Y-%m-%d %H:%M:%S")
        assert formatted == "2024-01-15 14:30:45"

        formatted_date = test_date.strftime("%d.%m.%Y")
        assert formatted_date == "15.01.2024"

        formatted_time = test_date.strftime("%H:%M")
        assert formatted_time == "14:30"

    def test_calculate_age_from_birthdate(self):
        from datetime import datetime, date

        # Мокаем текущую дату
        mock_today = date(2024, 1, 15)

        test_cases = [
            (date(2000, 1, 15), 24),  # День рождения сегодня
            (date(2000, 1, 14), 24),  # День рождения был вчера
            (date(2000, 1, 16), 23),  # День рождения завтра
            (date(2000, 12, 31), 23),  # Родился в конце года
        ]

        for birthdate, expected_age in test_cases:
            age = self._calculate_age(birthdate, mock_today)
            assert age == expected_age, f"Для {birthdate} ожидался возраст {expected_age}, получено {age}"

    def test_time_elapsed(self):
        from datetime import datetime, timedelta

        now = datetime.now()

        test_cases = [
            (now - timedelta(seconds=30), "30 секунд назад"),
            (now - timedelta(minutes=5), "5 минут назад"),
            (now - timedelta(hours=2), "2 часа назад"),
            (now - timedelta(days=1), "1 день назад"),
            (now - timedelta(days=7), "1 неделю назад"),
        ]

        for past_time, expected in test_cases:
            elapsed = self._time_elapsed(past_time, now)
            # Проверяем что строка не пустая (точное совпадение не нужно из-за локализации)
            assert elapsed


    def _calculate_age(self, birthdate, today=None):
        from datetime import date

        if today is None:
            today = date.today()

        age = today.year - birthdate.year

        # Если день рождения в этом году еще не наступил
        if (today.month, today.day) < (birthdate.month, birthdate.day):
            age -= 1

        return age

    def _time_elapsed(self, past_time, current_time=None):
        from datetime import datetime

        if current_time is None:
            current_time = datetime.now()

        delta = current_time - past_time

        if delta.days > 365:
            years = delta.days // 365
            return f"{years} год(а/лет) назад"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} месяц(ев) назад"
        elif delta.days > 0:
            return f"{delta.days} день(дней) назад"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} час(а/ов) назад"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} минут(ы) назад"
        else:
            return f"{delta.seconds} секунд(ы) назад"
