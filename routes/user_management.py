from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from flask_jwt_extended import get_jwt_identity
from models import db, User
from werkzeug.security import generate_password_hash

user_management_bp = Blueprint('user_management', __name__)


@user_management_bp.route('/api/register-staff', methods=['POST'])
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

@user_management_bp.route('/api/staff', methods=['GET'])
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
                "role": staff.role,
                "is_active": staff.is_active
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

@user_management_bp.route('/api/my-team/<int:staff_id>', methods=['PUT'])
@jwt_required()
def update_staff(staff_id):
    extra_claims = get_jwt()

    if extra_claims.get('role') != 'admin':
        return jsonify({
            "status": "error",
            "message": "صلاحية غير كافية, يجب ان تكون ادمن لتحديث بيانات الموظفين"
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({
            "status": "error",
            "message": "بيانات التحديث مطلوبة"
        }), 400

    staff = User.query.get(staff_id)
    current_admin_id = int(get_jwt_identity())
    if not staff or staff.parent_admin_id != current_admin_id:
        return jsonify({
            "status": "error",
            "message": "الموظف غير موجود أو لا يمكنك تحديثه"
        }), 404

    if 'username' in data:
        duplicate_staff = User.query.filter_by(username=data['username']).first()
        if duplicate_staff and duplicate_staff.id != staff.id:
            return jsonify({
                "status": "error",
                "message": "الاسم مأخوذ بالفعل"
            }), 400
        staff.username = data['username']

    if 'password' in data:
        staff.password_hash = generate_password_hash(data['password'])

    if 'role' in data:
        role = str(data['role']).strip().lower()
        if role not in ['viewer', 'commenter', 'editor']:
            return jsonify({
                "status": "error",
                "message": "الدور غير صالح"
            }), 400
        staff.role = role
    
    if 'is_active' in data:
        staff.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"تم تحديث بيانات الموظف '{staff.username}' بنجاح"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@user_management_bp.route('/api/my-team/<int:staff_id>', methods=['DELETE'])
@jwt_required()
def delete_staff(staff_id):
    extra_claims = get_jwt()

    if extra_claims.get('role') != 'admin':
        return jsonify({
            "status": "error",
            "message": "صلاحية غير كافية, يجب ان تكون ادمن لحذف الموظفين"
        }), 403

    staff = User.query.get(staff_id)
    if not staff or staff.parent_admin_id != get_jwt_identity():
        return jsonify({
            "status": "error",
            "message": "الموظف غير موجود أو لا يمكنك حذفه"
        }), 404

    try:
        db.session.delete(staff)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"تم حذف الموظف '{staff.username}' بنجاح"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500