from datetime import datetime

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import app, db
from models import Area, Subscriber, Transaction, User


def create_admin_token(admin):
    with app.app_context():
        return create_access_token(
            identity=str(admin.id),
            additional_claims={
                'username': admin.username,
                'role': 'admin',
                'admin_id': admin.id
            }
        )


def test_get_subscribers_combines_debt_and_last_renewal_filters(client):
    with app.app_context():
        admin = User(
            username='filter-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        area = Area(name='Zone A', admin_id=admin.id)
        db.session.add(area)
        db.session.flush()

        subscriber_old = Subscriber(
            name='Older Debt',
            phone_number='10001',
            area_id=area.id,
            balance=-4000
        )
        subscriber_recent = Subscriber(
            name='Recent Debt',
            phone_number='10002',
            area_id=area.id,
            balance=-2500
        )
        subscriber_paid = Subscriber(
            name='Paid User',
            phone_number='10003',
            area_id=area.id,
            balance=1500
        )
        db.session.add_all([subscriber_old, subscriber_recent, subscriber_paid])
        db.session.flush()

        db.session.add_all([
            Transaction(
                subscriber_id=subscriber_old.id,
                user_id=admin.id,
                transaction_type='renewal',
                amount=35000,
                transaction_date=datetime(2026, 1, 5, 12, 0, 0)
            ),
            Transaction(
                subscriber_id=subscriber_recent.id,
                user_id=admin.id,
                transaction_type='renewal',
                amount=35000,
                transaction_date=datetime(2026, 1, 20, 12, 0, 0)
            ),
            Transaction(
                subscriber_id=subscriber_paid.id,
                user_id=admin.id,
                transaction_type='renewal',
                amount=35000,
                transaction_date=datetime(2026, 1, 25, 12, 0, 0)
            )
        ])
        db.session.commit()

        token = create_admin_token(admin)

    response = client.get(
        '/api/subscribers?debt_only=true&renewal_from=2026-01-01&renewal_to=2026-01-31',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert [subscriber['name'] for subscriber in data['subscribers']] == ['Older Debt', 'Recent Debt']
    assert [subscriber['last_renewal_date'] for subscriber in data['subscribers']] == ['2026-01-05', '2026-01-20']


def test_get_subscribers_rejects_invalid_last_renewal_range(client):
    with app.app_context():
        admin = User(
            username='range-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

        token = create_admin_token(admin)

    response = client.get(
        '/api/subscribers?renewal_from=2026-02-10&renewal_to=2026-01-10',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data['status'] == 'error'


def test_get_logs_filters_by_single_subscriber_id(client):
    with app.app_context():
        admin = User(
            username='logs-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        staff = User(
            username='logs-staff',
            password_hash=generate_password_hash('123456'),
            role='staff',
            parent_admin_id=admin.id
        )
        db.session.add(staff)
        db.session.flush()

        area = Area(name='Zone B', admin_id=admin.id)
        db.session.add(area)
        db.session.flush()

        first_subscriber = Subscriber(
            name='Subscriber One',
            phone_number='20001',
            area_id=area.id,
            balance=0
        )
        second_subscriber = Subscriber(
            name='Subscriber Two',
            phone_number='20002',
            area_id=area.id,
            balance=0
        )
        db.session.add_all([first_subscriber, second_subscriber])
        db.session.flush()

        db.session.add_all([
            Transaction(
                subscriber_id=first_subscriber.id,
                user_id=admin.id,
                transaction_type='payment',
                amount=5000,
                transaction_date=datetime(2026, 2, 10, 9, 0, 0)
            ),
            Transaction(
                subscriber_id=first_subscriber.id,
                user_id=staff.id,
                transaction_type='renewal',
                amount=35000,
                transaction_date=datetime(2026, 2, 11, 9, 0, 0)
            ),
            Transaction(
                subscriber_id=second_subscriber.id,
                user_id=admin.id,
                transaction_type='payment',
                amount=6000,
                transaction_date=datetime(2026, 2, 12, 9, 0, 0)
            )
        ])
        db.session.commit()
        subscriber_id = first_subscriber.id
        token = create_admin_token(admin)

    response = client.get(
        f'/api/logs?subscriber_id={subscriber_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert [log['subscriber_name'] for log in data['logs']] == ['Subscriber One', 'Subscriber One']
    assert all(log['subscriber_id'] == subscriber_id for log in data['logs'])
    assert [log['processed_by'] for log in data['logs']] == ['logs-staff', 'logs-admin']


def test_update_area_name_by_owning_admin(client):
    with app.app_context():
        admin = User(
            username='area-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        area = Area(name='Old Area', admin_id=admin.id)
        db.session.add(area)
        db.session.commit()
        area_id = area.id
        token = create_admin_token(admin)

    response = client.put(
        f'/api/areas/{area_id}',
        json={'name': 'Updated Area'},
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['area']['name'] == 'Updated Area'