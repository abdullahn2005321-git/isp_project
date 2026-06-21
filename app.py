from flask import Flask
from flask_migrate import Migrate
from models import db
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

from routes.subscribers import subscribers_bp
from routes.payments import payments_bp
from routes.logging_and_reporting import logging_and_reporting_bp
from routes.auth import auth_bp

load_dotenv()

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
jwt = JWTManager(app)

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(subscribers_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(logging_and_reporting_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)