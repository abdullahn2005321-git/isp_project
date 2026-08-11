import os
from app import app
from models import db, User
from werkzeug.security import generate_password_hash

def seed_super_admin():
    with app.app_context():
        username = 'me'
        
        password = os.getenv('SUPER_ADMIN_PASSWORD')

        if not password:
            print("⚠️ خطأ: لم يتم العثور على كلمة المرور في ملف .env!")
            return

        existing_admin = User.query.filter_by(username=username).first()
        if existing_admin:
            print("⚠️ حساب المالك (السوبر أدمن) موجود بالفعل في قاعدة البيانات!")
            return

        super_admin = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='super_admin',
            parent_admin_id=None
        )

        try:
            db.session.add(super_admin)
            db.session.commit()
            print(f"✅ تم إنشاء الحساب الأعلى '{username}' بنجاح وبأمان تام!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ حدث خطأ: {str(e)}")

if __name__ == '__main__':
    seed_super_admin()