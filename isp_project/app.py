from flask import Flask
from flask_migrate import Migrate
from models import db
from flask_cors import CORS

from routes.subscribers import subscribers_bp
from routes.payments import payments_bp
from routes.logging_and_reporting import logging_and_reporting_bp

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1/isp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(subscribers_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(logging_and_reporting_bp)

if __name__ == '__main__':
    app.run(debug=True)