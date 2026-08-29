from flask import Flask, send_from_directory
from flask_migrate import Migrate
from models import db, DailyFinancialSummary
from flask_cors import CORS
import os
from datetime import timedelta
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

from routes.subscribers import subscribers_bp
from routes.transactions import transactions_bp
from routes.logging_and_reporting import logging_and_reporting_bp
from routes.auth import auth_bp
from routes.admins import admins_bp
from routes.user_management import user_management_bp

load_dotenv()

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@127.0.0.1/isp_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

db_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")

if db_url:
  # تصحيح بداية الرابط ليتوافق مع SQLAlchemy
  if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
else:
  # إذا لم يتوفر الرابط، يتم البناء تلقائياً من المتغيرات الفردية
  db_user = os.getenv("MYSQLUSER", "root")
  db_pass = os.getenv("MYSQLPASSWORD", "")
  db_host = os.getenv("MYSQLHOST", "127.0.0.1")
  db_port = os.getenv("MYSQLPORT", "3306")
  db_name = os.getenv("MYSQLDATABASE", "railway")
  db_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(subscribers_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(logging_and_reporting_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admins_bp)
app.register_blueprint(user_management_bp)



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
    app.run(host='0.0.0.0', port=port, debug=True)