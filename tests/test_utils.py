from unittest.mock import patch

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import app, db
from models import User


def test_unexpected_db_error_returns_generic_message_not_internal_details(client):
    with app.app_context():
        admin = User(
            username='error-path-admin',
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

    secret_detail = "table 'isp_db.areas' internal schema failure"

    with patch.object(db.session, 'commit', side_effect=RuntimeError(secret_detail)):
        response = client.post(
            '/api/areas',
            json={'name': 'Area That Fails To Save'},
            headers={'Authorization': f'Bearer {token}'}
        )

    data = response.get_json()

    assert response.status_code == 500
    assert data['status'] == 'error'
    assert secret_detail not in data['message']
