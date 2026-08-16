from flask import Blueprint,request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
@jwt_required(optional=True)
def register_admin():
    extra_claims = get_jwt() or {}
    existing_admin = User.query.filter_by(role='admin').first()

    if existing_admin and extra_claims.get('role') != 'super_admin':
        return jsonify({
            "status": "error",
            "message": "صلاحية غير كافية, يجب ان تكون سوبر ادمن لتسجيل الادمن"
        }), 403

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
    extra_claims = get_jwt()

    if extra_claims.get('role') != 'admin':
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
        }), 400

    role = str(data.get('role', 'viewer')).strip().lower()
    if role not in ['viewer', 'commenter', 'editor']:
        return jsonify({
            "status": "error",
            "message": "الدور غير صالح"
        }), 400

    current_admin_id = get_jwt_identity()

    new_staff = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role=role,
        parent_admin_id=current_admin_id
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

@auth_bp.route('/api/my-team', methods=['GET'])
@jwt_required()
def my_team():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({"status": "error", "message": "المستخدم غير موجود"}), 404

    if user.role == 'admin':
        manager = {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
        members = [
            {
                "id": staff.id,
                "username": staff.username,
                "role": staff.role
            }
            for staff in user.staff_members
        ]
    else:
        manager = None
        if user.manager:
            manager = {
                "id": user.manager.id,
                "username": user.manager.username,
                "role": user.manager.role
            }
        members = []

    return jsonify({
        "status": "success",
        "manager": manager,
        "members": members
    }), 200


@auth_bp.route('/api/admins', methods=['POST'])
@jwt_required()
def get_admins():
    try:
        extra_claims = get_jwt()
        if extra_claims.get('role') != 'super_admin':
            return jsonify({
                "status": "error",
                "message": "صلاحية غير كافية, يجب ان تكون سوبر ادمن لرؤية الادمنز"
            }), 403

        admins = User.query.filter_by(role='admin').all()
        admins_list = []
        for admin in admins:
            admins_list.append({
                "id": admin.id,
                "username": admin.username
            })
            
        return jsonify({
            "status": "success",
            "count": len(admins_list),
            "admins": admins_list
        }), 200
    
    except Exception as e:
        return jsonify({
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