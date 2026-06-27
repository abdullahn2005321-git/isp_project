import json

def test_register_admin_success(client):

    new_admin_data = {
        "username": "test_admin",
        "password": "123456"
    }

    response = client.post(
            '/api/register',
            data=json.dumps(new_admin_data),
            content_type='application/json'
    )
    
    data = json.loads(response.data.decode('utf-8'))

    assert response.status_code in [200,201]
    assert data['status'] == 'success'

def test_login_admin_success(client):

    new_admin_data = {
        "username": "test_admin",
        "password": "123456"
    }

    client.post(
            '/api/register',
            data=json.dumps(new_admin_data),
            content_type='application/json'
    )
    
    response = client.post(
        '/api/login',
        data=json.dumps(new_admin_data),
        content_type='application/json'
    )

    data = json.loads(response.data.decode('utf-8'))

    assert response.status_code == 200
    assert 'token' in data
