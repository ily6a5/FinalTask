from app import app as flask_app
import pytest
import sys
import os
import json
import tempfile

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def sample_user_data():
    return {
        "name": "Тестовый Пользователь",
        "email": "test@example.com",
        "age": 30,
        "phone": "+7 (999) 123-45-67",
        "city": "Тестовый Город"
    }

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
        }
    ]

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })
    yield flask_app


@pytest.fixture
def temp_users_file():
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.json',
        delete=False,
        encoding='utf-8'
    )

    test_users = [
        {
            "id": 1,
            "name": "Test User 1",
            "email": "test1@example.com",
            "age": 25,
            "phone": "+7 (999) 123-45-67",
            "city": "Test City",
            "created_at": "2024-01-15 10:00:00"
        },
        {
            "id": 2,
            "name": "Test User 2",
            "email": "test2@example.com",
            "age": 30,
            "phone": "+7 (999) 987-65-43",
            "city": "Another City",
            "created_at": "2024-01-16 12:00:00"
        }
    ]

    json.dump(test_users, temp_file, ensure_ascii=False, indent=2)
    temp_file.close()

    # Возвращаем путь к файлу
    yield temp_file.name

    # Очистка после теста
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def patch_file_path(monkeypatch):
    def _patch_file_path(file_path):
        import app
        original_path = app.users_file
        # Патчим глобальную переменную
        monkeypatch.setattr(app, 'users_file', file_path)

        # Возвращаем функцию для восстановления
        def restore():
            monkeypatch.setattr(app, 'users_file', original_path)

        return restore

    return _patch_file_path


@pytest.fixture
def app_with_temp_file(temp_users_file):
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

    from app import app as flask_app

    import app as app_module
    app_module.users_file = temp_users_file

    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })

    yield flask_app
