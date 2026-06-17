from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    subscribers = db.relationship('Subscriber', backref='area', lazy=True)


class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    parent_company_id = db.Column(db.String(50), nullable=True)
    balance = db.Column(db.Integer, default=0.0)
    promise_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    payments = db.relationship('Payment', backref='subscriber', lazy=True)
    renewals = db.relationship('Renewal', backref='subscriber', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscribers.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    payment_date = db.Column(db.DateTime, default=db.func.now())

class Renewal(db.Model):
    __tablename__ = 'renewals'
    id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscribers.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    renewal_date = db.Column(db.DateTime, default=db.func.now())

