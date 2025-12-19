import pytest
import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app import app as flask_app, load_users, save_users, users_file
except ImportError:
    from flask import Flask
    flask_app = Flask(__name__)
    
    users_file = 'users.json'
    
    def load_users():
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_users(users):
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True


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
    
    yield temp_file.name
    
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def app(temp_users_file):
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
    })
    
    import app as app_module
    original_path = getattr(app_module, 'users_file', 'users.json')
    app_module.users_file = temp_users_file
    
    yield flask_app
    
    app_module.users_file = original_path


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def patch_file_path(monkeypatch):
    def _patch_file_path(file_path):
        import app as app_module
        original_path = getattr(app_module, 'users_file', 'users.json')
        monkeypatch.setattr(app_module, 'users_file', file_path)
        
        def restore():
            monkeypatch.setattr(app_module, 'users_file', original_path)
        
        return restore
    
    return _patch_file_path


@pytest.fixture
def patch_users_file_context():
    import app as app_module
    
    class PatchFilePath:
        def __init__(self, file_path):
            self.file_path = file_path
            self.original_path = None
            
        def __enter__(self):
            self.original_path = app_module.users_file
            app_module.users_file = self.file_path
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            app_module.users_file = self.original_path
    
    return PatchFilePath
