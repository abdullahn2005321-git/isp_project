import pytest

from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:

        with app.app_context():

            db.create_all()

            yield client

            db.session.remove()
            
            db.drop_all()