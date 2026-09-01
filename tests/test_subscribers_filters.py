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
    assert data['pagination']['total_debt'] == 6500


def test_get_subscribers_returns_total_debt_beyond_current_page(client):
    with app.app_context():
        admin = User(
            username='debt-total-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        area = Area(name='Debt Total Zone', admin_id=admin.id)
        db.session.add(area)
        db.session.flush()

        db.session.add_all([
            Subscriber(name='First Debt', phone_number='10101', area_id=area.id, balance=-1000),
            Subscriber(name='Second Debt', phone_number='10102', area_id=area.id, balance=-2000),
            Subscriber(name='No Debt', phone_number='10103', area_id=area.id, balance=500)
        ])
        db.session.commit()
        token = create_admin_token(admin)

    response = client.get(
        '/api/subscribers?page=1&per_page=1',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert len(data['subscribers']) == 1
    assert data['pagination']['total_debt'] == 3000


def test_get_subscribers_defaults_to_latest_renewal_desc(client):
    with app.app_context():
        admin = User(
            username='default-order-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        area = Area(name='Zone B', admin_id=admin.id)
        db.session.add(area)
        db.session.flush()

        newest_subscriber = Subscriber(
            name='Newest Renewal',
            phone_number='20001',
            area_id=area.id,
            balance=0
        )
        mid_subscriber = Subscriber(
            name='Middle Renewal',
            phone_number='20002',
            area_id=area.id,
            balance=0
        )
        oldest_subscriber = Subscriber(
            name='Oldest Renewal',
            phone_number='20003',
            area_id=area.id,
            balance=0
        )
        db.session.add_all([newest_subscriber, mid_subscriber, oldest_subscriber])
        db.session.flush()

        db.session.add_all([
            Transaction(
                subscriber_id=newest_subscriber.id,
                user_id=admin.id,
                transaction_type='renewal',
                amount=35000,
                transaction_date=datetime(2026, 1, 25, 12, 0, 0)
            ),
            Transaction(
                subscriber_id=mid_subscriber.id,
                user_id=admin.id,
                transaction_type='renewal',
                amount=35000,
                transaction_date=datetime(2026, 1, 10, 12, 0, 0)
            ),
            Transaction(
                subscriber_id=oldest_subscriber.id,
                user_id=admin.id,
                transaction_type='renewal',
                amount=35000,
                transaction_date=datetime(2026, 1, 5, 12, 0, 0)
            )
        ])
        db.session.commit()

        token = create_admin_token(admin)

    response = client.get(
        '/api/subscribers',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert [subscriber['name'] for subscriber in data['subscribers']] == ['Oldest Renewal', 'Middle Renewal', 'Newest Renewal']


def test_get_subscribers_includes_legacy_rows_with_null_active_flag(client):
    with app.app_context():
        admin = User(
            username='legacy-data-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        area = Area(name='Legacy Zone', admin_id=admin.id)
        subscriber = Subscriber(
            name='Legacy Subscriber',
            phone_number='20008',
            area=area,
            balance=0,
            is_active=None
        )
        db.session.add_all([area, subscriber])
        db.session.commit()

        token = create_admin_token(admin)

    response = client.get(
        '/api/subscribers',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert [item['name'] for item in data['subscribers']] == ['Legacy Subscriber']


def test_get_subscribers_uses_logged_in_admin_when_claim_is_stale(client):
    with app.app_context():
        admin = User(
            username='owned-data-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        area = Area(name='Owned Zone', admin_id=admin.id)
        subscriber = Subscriber(
            name='Owned Subscriber',
            phone_number='20004',
            area=area,
            balance=0
        )
        db.session.add_all([area, subscriber])
        db.session.commit()

        token = create_access_token(
            identity=str(admin.id),
            additional_claims={
                'role': 'admin',
                'admin_id': 999999
            }
        )

    response = client.get(
        '/api/subscribers',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert [item['name'] for item in data['subscribers']] == ['Owned Subscriber']


def test_new_subscriber_without_renewal_appears_on_first_page(client):
    with app.app_context():
        admin = User(
            username='new-subscriber-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        area = Area(name='New Subscriber Zone', admin_id=admin.id)
        db.session.add(area)
        db.session.commit()

        token = create_admin_token(admin)
        area_id = area.id

    response = client.post(
        '/api/subscribers',
        json={
            'name': 'Just Added Subscriber',
            'phone_number': '20007',
            'area_id': area_id
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 201

    response = client.get(
        '/api/subscribers',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data['subscribers'][0]['name'] == 'Just Added Subscriber'


def test_get_areas_uses_logged_in_admin_when_claim_is_stale(client):
    with app.app_context():
        admin = User(
            username='owned-area-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()
        db.session.add(Area(name='Visible Zone', admin_id=admin.id))
        db.session.commit()

        token = create_access_token(
            identity=str(admin.id),
            additional_claims={'role': 'admin', 'admin_id': 999999}
        )

    response = client.get(
        '/api/areas',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert [area['name'] for area in data['areas']] == ['Visible Zone']


def test_payment_uses_logged_in_admin_when_claim_is_stale(client):
    with app.app_context():
        admin = User(
            username='payment-owner-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        area = Area(name='Payment Zone', admin_id=admin.id)
        subscriber = Subscriber(
            name='Payment Subscriber',
            phone_number='20005',
            area=area,
            balance=0
        )
        db.session.add_all([area, subscriber])
        db.session.commit()

        token = create_access_token(
            identity=str(admin.id),
            additional_claims={'role': 'admin', 'admin_id': 999999}
        )
        subscriber_id = subscriber.id

    response = client.post(
        '/api/transactions/payment',
        json={'subscriber_id': subscriber_id, 'amount': 5000},
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data['status'] == 'success'


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


def test_get_logs_uses_logged_in_admin_when_claim_is_stale(client):
    with app.app_context():
        admin = User(
            username='logs-owner-admin',
            password_hash=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()

        area = Area(name='Logs Zone', admin_id=admin.id)
        subscriber = Subscriber(
            name='Logs Subscriber',
            phone_number='20006',
            area=area,
            balance=0
        )
        db.session.add_all([area, subscriber])
        db.session.flush()
        db.session.add(Transaction(
            subscriber_id=subscriber.id,
            user_id=admin.id,
            transaction_type='payment',
            amount=5000,
            transaction_date=datetime(2026, 2, 15, 9, 0, 0)
        ))
        db.session.commit()

        token = create_access_token(
            identity=str(admin.id),
            additional_claims={'role': 'admin', 'admin_id': 999999}
        )

    response = client.get(
        '/api/logs',
        headers={'Authorization': f'Bearer {token}'}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert [log['subscriber_name'] for log in data['logs']] == ['Logs Subscriber']


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