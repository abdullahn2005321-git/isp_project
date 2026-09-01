from datetime import date

from flask_jwt_extended import create_access_token

from app import app, db
from models import Area, DailyFinancialSummary, Subscriber, Transaction, User
from tasks.daily_summary import generate_multi_admin_daily_summary


def test_daily_summary_counts_legacy_payment_without_method_as_cash(client):
    target_date = date(2026, 9, 1)

    with app.app_context():
        admin = User(username='summary-admin', password_hash='hash', role='admin')
        db.session.add(admin)
        db.session.flush()

        area = Area(name='summary-area', admin_id=admin.id)
        db.session.add(area)
        db.session.flush()

        subscriber = Subscriber(
            name='summary-subscriber',
            phone_number='07700000001',
            area_id=area.id,
        )
        db.session.add(subscriber)
        db.session.flush()

        db.session.add_all([
            Transaction(
                subscriber_id=subscriber.id,
                user_id=admin.id,
                transaction_type='payment',
                payment_method='electronic',
                amount=630_000,
                transaction_date=target_date,
            ),
            Transaction(
                subscriber_id=subscriber.id,
                user_id=admin.id,
                transaction_type='payment',
                amount=350_000,
                transaction_date=target_date,
            ),
        ])
        db.session.commit()

        generate_multi_admin_daily_summary(target_date)

        summary = DailyFinancialSummary.query.filter_by(
            summary_date=target_date,
            admin_id=admin.id,
        ).one()

        assert summary.cash_received == 350_000
        assert summary.electronic_received == 630_000
        assert summary.total_collected == 980_000


def test_cash_renewal_stores_cash_payment_method(client):
    with app.app_context():
        admin = User(username='renewal-admin', password_hash='hash', role='admin')
        db.session.add(admin)
        db.session.flush()

        area = Area(name='renewal-area', admin_id=admin.id)
        db.session.add(area)
        db.session.flush()

        subscriber = Subscriber(
            name='renewal-subscriber',
            phone_number='07700000002',
            area_id=area.id,
        )
        db.session.add(subscriber)
        db.session.commit()
        subscriber_id = subscriber.id

        token = create_access_token(
            identity=str(admin.id),
            additional_claims={'role': 'admin', 'admin_id': admin.id},
        )

    response = client.post(
        '/api/transactions/renewal',
        json={
            'subscriber_id': subscriber_id,
            'amount': 350_000,
            'is_cash': True,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 201

    with app.app_context():
        payment = Transaction.query.filter_by(transaction_type='payment').one()
        assert payment.payment_method == 'cash'