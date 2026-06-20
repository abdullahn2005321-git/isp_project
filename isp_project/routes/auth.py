from flask import Blueprint,request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register_admin():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            "status": "error",
            "message": "اسم المستخدم وكلمه المرور مطلوبان"
        }), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            "status": "error",
            "message": "اسم المستخدم مسجل مسبقا"
        }), 400
    new_admin = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role='admin',
        parent_admin_id=None
    )
    try:
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "تم تسجيل الادمن بنجاح, يمكنك الان تسجيل الدخول"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@auth_bp.route('/api/register-staff', methods=['POST'])
@jwt_required()
def register_staff():
    current_user = get_jwt_identity()

    if current_user.get('role') != 'admin':
        return jsonify({
            "status": "error",
            "message": "صلاحية غير كافية, يجب ان تكون ادمن لتوظيف الموظفين"
        }), 403
    
    data = request.get_json()

    if not data or not 'username' in data or not 'password' in data:
        return jsonify({
            "status": "error",
            "message": "اسم المستخدم وكلمه المرور للموظف مطلوبان"
        }), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            "status": "error",
            "message": "الاسم مأخوذ بالفعل"
        })

    new_staff = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role='staff',
        parent_admin_id=current_user.get('user_id')
    )
    try:
        db.session.add(new_staff)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"تم تسجيل الموظف '{new_staff.username}' بنجاح تحت إشرافك"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify ({
            "status": "error",
            "message": str(e)
        }), 500

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

        target_admin_id = user.id if user.role == 'admin' else user.parent_admin_id

        token_identity = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "admin_id": target_admin_id
        }

        access_token = create_access_token(identity=token_identity)

        return jsonify({
            "status": "success",
            "message": "تم تسجيل بنجاح",
            "token": access_token,
            "role": user.role,
            "username": user.username
        }), 200
    
    else:
        return jsonify({
            "status": "error",
            "message": "اسم المستخدم أو كلمة المرور خاطئة"
        }), 401