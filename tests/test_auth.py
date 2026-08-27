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
            '/api/admins',
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
            '/api/admins',
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


def test_viewer_cannot_process_payment(client):
    with app.app_context():
        admin = User(
            username='viewer-owner-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        viewer = User(
            username='viewer-member',
            password_hash=generate_password_hash('123456'),
            role='viewer',
            parent_admin_id=admin.id
        )
        db.session.add(viewer)
        db.session.commit()

        token = create_access_token(
            identity=str(viewer.id),
            additional_claims={
                'role': 'viewer',
                'admin_id': admin.id
            }
        )

    response = client.post(
        '/api/transactions/payment',
        json={'subscriber_id': 1, 'amount': 5000},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403


def test_commenter_cannot_process_payment(client):
    with app.app_context():
        admin = User(
            username='commenter-owner-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        commenter = User(
            username='commenter-member',
            password_hash=generate_password_hash('123456'),
            role='commenter',
            parent_admin_id=admin.id
        )
        db.session.add(commenter)
        db.session.commit()

        token = create_access_token(
            identity=str(commenter.id),
            additional_claims={
                'role': 'commenter',
                'admin_id': admin.id
            }
        )

    response = client.post(
        '/api/transactions/payment',
        json={'subscriber_id': 1, 'amount': 5000},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403


def test_register_admin_requires_super_admin_after_first_admin(client):
    with app.app_context():
        existing_admin = User(
            username='existing-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(existing_admin)
        db.session.commit()

        token = create_access_token(
            identity=str(existing_admin.id),
            additional_claims={
                'role': 'admin',
                'admin_id': existing_admin.id
            }
        )

    response = client.post(
        '/api/admins',
        json={'username': 'second-admin', 'password': '123456'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    assert response.get_json()['status'] == 'error'


def test_admin_can_list_own_team(client):
    with app.app_context():
        admin = User(
            username='team-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        staff = User(
            username='team-viewer',
            password_hash=generate_password_hash('123456'),
            role='viewer',
            parent_admin_id=admin.id
        )
        db.session.add(staff)
        db.session.commit()
        admin_id = admin.id
        staff_id = staff.id

        token = create_access_token(
            identity=str(admin_id),
            additional_claims={
                'role': 'admin',
                'admin_id': admin_id
            }
        )

    response = client.get(
        '/api/staff',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data['manager']['id'] == admin_id
    assert data['members'] == [{
        'id': staff_id,
        'username': 'team-viewer',
        'role': 'viewer',
        'is_active': True
    }]


def test_admin_cannot_update_another_admins_staff(client):
    with app.app_context():
        first_admin = User(
            username='first-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        second_admin = User(
            username='second-owner-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add_all([first_admin, second_admin])
        db.session.flush()

        staff = User(
            username='protected-staff',
            password_hash=generate_password_hash('123456'),
            role='editor',
            parent_admin_id=second_admin.id
        )
        db.session.add(staff)
        db.session.commit()
        first_admin_id = first_admin.id
        staff_id = staff.id

        token = create_access_token(
            identity=str(first_admin_id),
            additional_claims={
                'role': 'admin',
                'admin_id': first_admin_id
            }
        )

    response = client.put(
        f'/api/my-team/{staff_id}',
        json={'role': 'viewer'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 404

    with app.app_context():
        assert User.query.get(staff_id).role == 'editor'


def test_admin_can_update_staff_without_changing_username(client):
    with app.app_context():
        admin = User(
            username='update-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        staff = User(
            username='unchanged-staff',
            password_hash=generate_password_hash('123456'),
            role='editor',
            parent_admin_id=admin.id
        )
        db.session.add(staff)
        db.session.commit()
        admin_id = admin.id
        staff_id = staff.id

        token = create_access_token(
            identity=str(admin_id),
            additional_claims={'role': 'admin', 'admin_id': admin_id}
        )

    response = client.put(
        f'/api/my-team/{staff_id}',
        json={'username': 'unchanged-staff', 'role': 'viewer', 'is_active': False},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

    with app.app_context():
        updated_staff = User.query.get(staff_id)
        assert updated_staff.role == 'viewer'
        assert updated_staff.is_active is False
