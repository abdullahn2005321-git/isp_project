from datetime import date

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import app, db
from models import Area, Subscriber, User


def _make_admin(username):
    admin = User(
        username=username,
        password_hash=generate_password_hash('123456'),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    return admin.id


def _token_for(user_id, role, admin_id):
    return create_access_token(
        identity=str(user_id),
        additional_claims={'role': role, 'admin_id': admin_id}
    )


def test_add_area_missing_name_rejected(client):
    with app.app_context():
        admin_id = _make_admin('area-owner-admin')
        token = _token_for(admin_id, 'admin', admin_id)

    response = client.post(
        '/api/areas',
        json={'name': '   '},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400


def test_add_area_forbidden_for_viewer(client):
    with app.app_context():
        admin_id = _make_admin('area-viewer-owner-admin')
        viewer = User(
            username='area-viewer',
            password_hash=generate_password_hash('123456'),
            role='viewer',
            parent_admin_id=admin_id
        )
        db.session.add(viewer)
        db.session.commit()
        token = _token_for(viewer.id, 'viewer', admin_id)

    response = client.post(
        '/api/areas',
        json={'name': 'New Area'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403


def test_update_area_owned_by_another_admin_rejected(client):
    with app.app_context():
        owner_admin_id = _make_admin('area-real-owner-admin')
        other_admin_id = _make_admin('area-intruder-admin')

        area = Area(name='Owned Area', admin_id=owner_admin_id)
        db.session.add(area)
        db.session.commit()
        area_id = area.id

        token = _token_for(other_admin_id, 'admin', other_admin_id)

    response = client.put(
        f'/api/areas/{area_id}',
        json={'name': 'Hijacked Name'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403


def test_add_subscriber_missing_fields_rejected(client):
    with app.app_context():
        admin_id = _make_admin('sub-missing-fields-admin')
        token = _token_for(admin_id, 'admin', admin_id)

    response = client.post(
        '/api/subscribers',
        json={'name': 'No Phone Or Area'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400


def test_add_subscriber_area_not_owned_rejected(client):
    with app.app_context():
        owner_admin_id = _make_admin('sub-area-owner-admin')
        other_admin_id = _make_admin('sub-area-intruder-admin')

        area = Area(name='Someone Elses Area', admin_id=owner_admin_id)
        db.session.add(area)
        db.session.commit()
        area_id = area.id

        token = _token_for(other_admin_id, 'admin', other_admin_id)

    response = client.post(
        '/api/subscribers',
        json={'name': 'X', 'phone_number': '07700000001', 'area_id': area_id},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403


def test_add_subscriber_duplicate_phone_number_rejected(client):
    with app.app_context():
        admin_id = _make_admin('sub-dup-phone-admin')
        area = Area(name='Dup Phone Area', admin_id=admin_id)
        db.session.add(area)
        db.session.commit()
        area_id = area.id
        token = _token_for(admin_id, 'admin', admin_id)

    payload = {'name': 'First', 'phone_number': '07711112222', 'area_id': area_id}
    client.post('/api/subscribers', json=payload, headers={'Authorization': f'Bearer {token}'})

    response = client.post(
        '/api/subscribers',
        json={'name': 'Second', 'phone_number': '07711112222', 'area_id': area_id},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400


def test_get_subscriber_by_id_success(client):
    with app.app_context():
        admin_id = _make_admin('sub-get-single-admin')
        area = Area(name='Get Single Area', admin_id=admin_id)
        db.session.add(area)
        db.session.commit()

        sub = Subscriber(name='Solo Sub', phone_number='07700001111', area_id=area.id)
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id

        token = _token_for(admin_id, 'admin', admin_id)

    response = client.get(
        f'/api/subscribers/{sub_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data['subscriber']['id'] == sub_id
    assert data['subscriber']['name'] == 'Solo Sub'


def test_get_subscriber_by_id_isolated_between_admins(client):
    with app.app_context():
        owner_admin_id = _make_admin('sub-get-owner-admin')
        other_admin_id = _make_admin('sub-get-intruder-admin')

        area = Area(name='Isolated Area', admin_id=owner_admin_id)
        db.session.add(area)
        db.session.commit()

        sub = Subscriber(name='Hidden Sub', phone_number='07700002222', area_id=area.id)
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id

        token = _token_for(other_admin_id, 'admin', other_admin_id)

    response = client.get(
        f'/api/subscribers/{sub_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 404


def test_update_subscriber_rejects_unowned_area(client):
    with app.app_context():
        admin_id = _make_admin('sub-update-area-admin')
        other_admin_id = _make_admin('sub-update-area-intruder')

        own_area = Area(name='Own Area', admin_id=admin_id)
        foreign_area = Area(name='Foreign Area', admin_id=other_admin_id)
        db.session.add_all([own_area, foreign_area])
        db.session.commit()

        sub = Subscriber(name='Movable Sub', phone_number='07700003333', area_id=own_area.id)
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id
        foreign_area_id = foreign_area.id

        token = _token_for(admin_id, 'admin', admin_id)

    response = client.put(
        f'/api/subscribers/{sub_id}',
        json={'area_id': foreign_area_id},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 404


def test_update_subscriber_clears_promise_date_when_blank(client):
    with app.app_context():
        admin_id = _make_admin('sub-clear-promise-admin')
        area = Area(name='Promise Area', admin_id=admin_id)
        db.session.add(area)
        db.session.commit()

        sub = Subscriber(
            name='Promised Sub',
            phone_number='07700004444',
            area_id=area.id,
            promise_date=date(2026, 1, 1)
        )
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id

        token = _token_for(admin_id, 'admin', admin_id)

    response = client.put(
        f'/api/subscribers/{sub_id}',
        json={'promise_date': ''},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Subscriber, sub_id).promise_date is None


def test_delete_subscriber_forbidden_for_commenter(client):
    with app.app_context():
        admin_id = _make_admin('sub-delete-commenter-admin')
        commenter = User(
            username='sub-delete-commenter',
            password_hash=generate_password_hash('123456'),
            role='commenter',
            parent_admin_id=admin_id
        )
        db.session.add(commenter)
        db.session.commit()

        area = Area(name='Delete Perm Area', admin_id=admin_id)
        db.session.add(area)
        db.session.commit()

        sub = Subscriber(name='Untouchable Sub', phone_number='07700005555', area_id=area.id)
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id

        token = _token_for(commenter.id, 'commenter', admin_id)

    response = client.delete(
        f'/api/subscribers/{sub_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403


def test_delete_subscriber_blocked_when_balance_nonzero(client):
    with app.app_context():
        admin_id = _make_admin('sub-delete-balance-admin')
        area = Area(name='Balance Block Area', admin_id=admin_id)
        db.session.add(area)
        db.session.commit()

        sub = Subscriber(name='Indebted Sub', phone_number='07700006666', area_id=area.id, balance=-5000)
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id

        token = _token_for(admin_id, 'admin', admin_id)

    response = client.delete(
        f'/api/subscribers/{sub_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400

    with app.app_context():
        assert db.session.get(Subscriber, sub_id).is_active is True


def test_delete_subscriber_success_soft_deletes(client):
    with app.app_context():
        admin_id = _make_admin('sub-delete-success-admin')
        area = Area(name='Clean Delete Area', admin_id=admin_id)
        db.session.add(area)
        db.session.commit()

        sub = Subscriber(name='Settled Sub', phone_number='07700007777', area_id=area.id, balance=0)
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id

        token = _token_for(admin_id, 'admin', admin_id)

    response = client.delete(
        f'/api/subscribers/{sub_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Subscriber, sub_id).is_active is False

    follow_up = client.get(
        f'/api/subscribers/{sub_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert follow_up.status_code == 404
