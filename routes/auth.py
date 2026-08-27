from flask import Blueprint,request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            "status": "error",
            "message": "اسم المستخدم وكلمه المرور مطلوبان"
        }), 400
    
    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password_hash, data['password']):

        user_role = str(user.role or 'viewer').strip().lower()
        if user_role not in ['super_admin', 'admin', 'commenter', 'editor', 'viewer']:
            user_role = 'viewer'

        target_admin_id = user.id if user_role == 'admin' else user.parent_admin_id

        extra_data = {
            "username": user.username,
            "role": user_role,
            "admin_id": target_admin_id
        }

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=extra_data
        )

        return jsonify({
            "status": "success",
            "message": "تم تسجيل بنجاح",
            "token": access_token,
            "role": user_role,
            "username": user.username
        }), 200
    
    else:
        return jsonify({
            "status": "error",
            "message": "اسم المستخدم أو كلمة المرور خاطئة"
        }), 401