import json

from flask_jwt_extended import create_access_token

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

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


def test_register_staff_accepts_new_role(client):
    with app.app_context():
        admin = User(
            username='staff-role-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

        token = create_access_token(
            identity=str(admin.id),
            additional_claims={
                'role': 'admin',
                'admin_id': admin.id
            }
        )

    response = client.post(
        '/api/register-staff',
        json={
            'username': 'editor-member',
            'password': '123456',
            'role': 'editor'
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 201

    with app.app_context():
        staff = User.query.filter_by(username='editor-member').first()
        assert staff is not None
        assert staff.role == 'editor'
