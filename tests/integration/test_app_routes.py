import pytest
import json


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.data.decode('utf-8', errors='ignore')
    assert response.status_code == 200


def test_users_page(client):
    response = client.get('/users')
    assert response.status_code == 200


def test_add_user_page(client):
    response = client.get('/users/add')
    assert response.status_code == 200
    data = response.data.decode('utf-8', errors='ignore')
    assert 'form' in data.lower()


def test_api_users(client):
    response = client.get('/api/users')
    assert response.status_code == 200
    assert response.content_type == 'application/json'


def test_about_page(client):
    response = client.get('/about')
    assert response.status_code == 200


def test_contact_page(client):
    response = client.get('/contact')
    assert response.status_code == 200


def test_contact_form_submission(client):
    form_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'message': 'Test message'
    }

    response = client.post('/contact', data=form_data, follow_redirects=True)
    assert response.status_code == 200
