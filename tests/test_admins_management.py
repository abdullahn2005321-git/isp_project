from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, db
from models import User


def _make_super_admin():
    super_admin = User(
        username='root-super-admin',
        password_hash=generate_password_hash('123456'),
        role='super_admin'
    )
    db.session.add(super_admin)
    db.session.commit()
    return super_admin.id


def test_get_admins_requires_super_admin(client):
    with app.app_context():
        admin = User(
            username='plain-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id

        token = create_access_token(
            identity=str(admin_id),
            additional_claims={'role': 'admin', 'admin_id': admin_id}
        )

    response = client.get('/api/admins', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 403


def test_super_admin_can_list_admins(client):
    with app.app_context():
        super_admin_id = _make_super_admin()

        first_admin = User(
            username='listed-admin-one',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        second_admin = User(
            username='listed-admin-two',
            password_hash=generate_password_hash('123456'),
            role='admin',
            is_active=False
        )
        db.session.add_all([first_admin, second_admin])
        db.session.commit()

        token = create_access_token(
            identity=str(super_admin_id),
            additional_claims={'role': 'super_admin'}
        )

    response = client.get('/api/admins', headers={'Authorization': f'Bearer {token}'})
    data = response.get_json()

    assert response.status_code == 200
    statuses = {a['username']: a['is_active'] for a in data['admins']}
    assert statuses['listed-admin-one'] is True
    assert statuses['listed-admin-two'] is False


def test_update_admin_requires_super_admin(client):
    with app.app_context():
        admin = User(
            username='non-super-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id

        token = create_access_token(
            identity=str(admin_id),
            additional_claims={'role': 'admin', 'admin_id': admin_id}
        )

    response = client.put(
        f'/api/admins/{admin_id}',
        json={'is_active': False},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403


def test_update_admin_updates_username_password_and_active_status(client):
    with app.app_context():
        super_admin_id = _make_super_admin()

        target_admin = User(
            username='before-update-admin',
            password_hash=generate_password_hash('old-password'),
            role='admin'
        )
        db.session.add(target_admin)
        db.session.commit()
        target_admin_id = target_admin.id

        token = create_access_token(
            identity=str(super_admin_id),
            additional_claims={'role': 'super_admin'}
        )

    response = client.put(
        f'/api/admins/{target_admin_id}',
        json={
            'username': 'after-update-admin',
            'password': 'new-password',
            'is_active': False
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

    with app.app_context():
        updated = db.session.get(User, target_admin_id)
        assert updated.username == 'after-update-admin'
        assert updated.is_active is False
        assert check_password_hash(updated.password_hash, 'new-password')


def test_update_admin_rejects_duplicate_username(client):
    with app.app_context():
        super_admin_id = _make_super_admin()

        first_admin = User(
            username='taken-username-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        second_admin = User(
            username='second-admin-to-rename',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add_all([first_admin, second_admin])
        db.session.commit()
        second_admin_id = second_admin.id

        token = create_access_token(
            identity=str(super_admin_id),
            additional_claims={'role': 'super_admin'}
        )

    response = client.put(
        f'/api/admins/{second_admin_id}',
        json={'username': 'taken-username-admin'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400


def test_update_admin_not_found(client):
    with app.app_context():
        super_admin_id = _make_super_admin()
        token = create_access_token(
            identity=str(super_admin_id),
            additional_claims={'role': 'super_admin'}
        )

    response = client.put(
        '/api/admins/999999',
        json={'is_active': False},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 404
