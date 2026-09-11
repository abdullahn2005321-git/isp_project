from datetime import date, datetime

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import app, db
from models import Area, DailyFinancialSummary, Subscriber, Transaction, User


def make_token(user, role=None):
    resolved_role = role or user.role
    return create_access_token(
        identity=str(user.id),
        additional_claims={
            'username': user.username,
            'role': resolved_role,
            'admin_id': user.id if resolved_role == 'admin' else user.parent_admin_id,
        },
    )


def create_admin(username):
    admin = User(
        username=username,
        password_hash=generate_password_hash('123456'),
        role='admin',
    )
    db.session.add(admin)
    db.session.flush()
    return admin


def create_staff(username, role, admin_id):
    staff = User(
        username=username,
        password_hash=generate_password_hash('123456'),
        role=role,
        parent_admin_id=admin_id,
    )
    db.session.add(staff)
    db.session.flush()
    return staff


def test_monthly_summary_allows_admin_and_editor_but_rejects_viewer(client):
    with app.app_context():
        admin = create_admin('monthly-owner')
        editor = create_staff('monthly-editor', 'editor', admin.id)
        viewer = create_staff('monthly-viewer', 'viewer', admin.id)
        db.session.add(DailyFinancialSummary(
            admin_id=admin.id,
            summary_date=date(2026, 9, 5),
            renewals_count=2,
            total_renewals_amount=70_000,
            payments_count=3,
            cash_received=20_000,
            electronic_received=10_000,
            total_collected=30_000,
            total_transactions_count=5,
        ))
        db.session.commit()
        editor_token = make_token(editor)
        viewer_token = make_token(viewer)
        admin_token = make_token(admin)

    for token in (admin_token, editor_token):
        response = client.get(
            '/api/monthly-summary?year=2026&month=9',
            headers={'Authorization': f'Bearer {token}'},
        )
        data = response.get_json()
        assert response.status_code == 200
        assert data['success'] is True
        assert data['totals']['grand_total_collected'] == 30_000
        assert data['days'][0]['summary_date'] == '2026-09-05'

    response = client.get(
        '/api/monthly-summary?year=2026&month=9',
        headers={'Authorization': f'Bearer {viewer_token}'},
    )
    assert response.status_code == 403


def test_monthly_summary_isolated_between_admins(client):
    with app.app_context():
        first_admin = create_admin('monthly-first-owner')
        second_admin = create_admin('monthly-second-owner')
        db.session.add_all([
            DailyFinancialSummary(
                admin_id=first_admin.id,
                summary_date=date(2026, 9, 6),
                total_collected=11_000,
            ),
            DailyFinancialSummary(
                admin_id=second_admin.id,
                summary_date=date(2026, 9, 6),
                total_collected=99_000,
            ),
        ])
        db.session.commit()
        token = make_token(first_admin)
        second_admin_id = second_admin.id

    response = client.get(
        '/api/monthly-summary?year=2026&month=9',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data['totals']['grand_total_collected'] == 11_000
    assert data['admin_id'] != second_admin_id


def test_daily_report_uses_new_route_and_filters_by_admin(client):
    target_date = datetime(2026, 9, 7, 10, 0, 0)
    with app.app_context():
        first_admin = create_admin('daily-first-owner')
        second_admin = create_admin('daily-second-owner')
        first_area = Area(name='Daily First Area', admin_id=first_admin.id)
        second_area = Area(name='Daily Second Area', admin_id=second_admin.id)
        db.session.add_all([first_area, second_area])
        db.session.flush()
        first_subscriber = Subscriber(
            name='Daily First Subscriber',
            phone_number='07700001001',
            area_id=first_area.id,
        )
        second_subscriber = Subscriber(
            name='Daily Second Subscriber',
            phone_number='07700001002',
            area_id=second_area.id,
        )
        db.session.add_all([first_subscriber, second_subscriber])
        db.session.flush()
        db.session.add_all([
            Transaction(
                subscriber_id=first_subscriber.id,
                user_id=first_admin.id,
                transaction_type='payment',
                amount=5_000,
                transaction_date=target_date,
            ),
            Transaction(
                subscriber_id=first_subscriber.id,
                user_id=first_admin.id,
                transaction_type='renewal',
                amount=35_000,
                transaction_date=target_date,
            ),
            Transaction(
                subscriber_id=second_subscriber.id,
                user_id=second_admin.id,
                transaction_type='payment',
                amount=99_000,
                transaction_date=target_date,
            ),
        ])
        db.session.commit()
        token = make_token(first_admin)

    response = client.get(
        '/api/daily_payment_and_renewal_report?date=2026-09-07',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data['target_date'] == '2026-09-07'
    assert data['summary']['total_payments_collected'] == 5_000
    assert data['summary']['total_renewals_value'] == 35_000
    assert data['summary']['payments_count'] == 1
    assert data['summary']['renewals_count'] == 1


def test_commenter_can_update_notes_but_viewer_cannot(client):
    with app.app_context():
        admin = create_admin('notes-owner')
        commenter = create_staff('notes-commenter', 'commenter', admin.id)
        viewer = create_staff('notes-viewer', 'viewer', admin.id)
        area = Area(name='Notes Area', admin_id=admin.id)
        db.session.add(area)
        db.session.flush()
        subscriber = Subscriber(
            name='Notes Subscriber',
            phone_number='07700002001',
            area_id=area.id,
            notes='old note',
        )
        db.session.add(subscriber)
        db.session.commit()
        subscriber_id = subscriber.id
        commenter_token = make_token(commenter)
        viewer_token = make_token(viewer)

    response = client.put(
        f'/api/subscribers/{subscriber_id}',
        json={'notes': 'updated directly'},
        headers={'Authorization': f'Bearer {commenter_token}'},
    )
    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Subscriber, subscriber_id).notes == 'updated directly'

    response = client.put(
        f'/api/subscribers/{subscriber_id}',
        json={'notes': 'viewer must not update'},
        headers={'Authorization': f'Bearer {viewer_token}'},
    )
    assert response.status_code == 403

    with app.app_context():
        assert db.session.get(Subscriber, subscriber_id).notes == 'updated directly'
