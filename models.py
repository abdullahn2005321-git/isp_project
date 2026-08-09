from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='staff')
    parent_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    staff_members = db.relationship('User', backref=db.backref('manager', remote_side=[id]), lazy=True)

class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin = db.relationship('User', backref=db.backref('areas', lazy=True))
    subscribers = db.relationship('Subscriber', backref='area', lazy=True)

class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    balance = db.Column(db.Integer, default=0)
    promise_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    transactions = db.relationship('Transaction', backref='subscriber', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscribers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'payment' or 'renewal'
    amount = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.DateTime, default=db.func.now())
    processed_by = db.relationship('User', backref='processed_transactions', lazy=True)