from flask import Flask, send_from_directory, jsonify
from flask_migrate import Migrate
from models import db
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@127.0.0.1/isp_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
jwt = JWTManager(app)

try:
    db.init_app(app)
except Exception:
    logger.exception("Failed to initialize the database (db.init_app)")

try:
    migrate = Migrate(app, db)
except Exception:
    logger.exception("Failed to initialize Flask-Migrate")

try:
    from routes.subscribers import subscribers_bp
    app.register_blueprint(subscribers_bp)
except Exception:
    logger.exception("Failed to register subscribers_bp blueprint")

try:
    from routes.transactions import transactions_bp
    app.register_blueprint(transactions_bp)
except Exception:
    logger.exception("Failed to register transactions_bp blueprint")

try:
    from routes.logging_and_reporting import logging_and_reporting_bp
    app.register_blueprint(logging_and_reporting_bp)
except Exception:
    logger.exception("Failed to register logging_and_reporting_bp blueprint")

try:
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
except Exception:
    logger.exception("Failed to register auth_bp blueprint")


@app.route('/health')
def health_check():
    # Simple health check that does not touch the database, so it can
    # confirm the process is up even if DB initialization/migrations fail.
    return jsonify({'status': 'ok'})

# ==========================================
# مسارات تشغيل الواجهة الأمامية (Frontend)
# ==========================================

# 1. مسار الرابط الرئيسي (عرض صفحة الدخول)
@app.route('/')
def serve_frontend():
    # سيقوم السيرفر بفتح مجلد frontend وعرض ملف index.html
    return send_from_directory('frontend', 'index.html')

# 2. مسار لجلب باقي الملفات (CSS, JavaScript, الصور) لكي تعمل الواجهة بشكل سليم
@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('frontend', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)