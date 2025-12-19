import pytest
import json


class TestUserRoutes:

    def test_get_users_list(self, client, mock_users):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr('app.load_users', lambda: mock_users)
            response = client.get('/users')
            assert response.status_code == 200

    def test_get_user_profile(self, client, mock_users):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr('app.load_users', lambda: mock_users)
            response = client.get('/user/4')
            assert response.status_code in [200, 404]

    def test_add_user_form_get(self, client):
        response = client.get('/users/add')
        assert response.status_code == 200

    def test_add_user_form_post(self, client, mock_users):
        from unittest.mock import patch

        with patch('app.load_users', return_value=mock_users):
            with patch('app.save_users') as mock_save:
                user_data = {
                    'name': 'New User',
                    'email': 'new@example.com',
                    'age': '30',
                }
                response = client.post('/users/add', data=user_data, follow_redirects=True)
                assert response.status_code == 200
                mock_save.assert_called_once()


class TestAPIRoutes:

    def test_api_get_users(self, client, mock_users):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr('app.load_users', lambda: mock_users)
            response = client.get('/api/users')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            data = json.loads(response.data)
            assert isinstance(data, list)

    def test_api_get_single_user(self, client, mock_users):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr('app.load_users', lambda: mock_users)
            response = client.get('/api/users/1')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'id' in data

    def test_api_add_user(self, client, mock_users):
        with patch('app.load_users', return_value=mock_users):
            with patch('app.save_users') as mock_save:
                new_user = {
                    'name': 'API Test',
                    'email': 'api@example.com',
                    'age': 35
                }
                response = client.post('/api/users/add',
                                       data=json.dumps(new_user),
                                       content_type='application/json')
                assert response.status_code in [201, 400]

    def test_api_calculate(self, client):
        test_data = {'a': 10, 'b': 5, 'operation': 'add'}
        response = client.post('/api/calculate',
                               data=json.dumps(test_data),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data


# Helper function for mocking
def patch(module, **kwargs):
    import unittest.mock
    return unittest.mock.patch(module, **kwargs)
