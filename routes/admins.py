from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash
from models import db, User

admins_bp = Blueprint('admins', __name__)

@admins_bp.route('/api/admins', methods=['POST'])
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


@admins_bp.route('/api/admins', methods=['GET'])
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
                "username": admin.username,
                "is_active": admin.is_active
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

@admins_bp.route('/api/admins/<int:admin_id>', methods=['PUT'])
@jwt_required()
def update_admin(admin_id):
    extra_claims = get_jwt()
    if extra_claims.get('role') != 'super_admin':
        return jsonify({
            "status": "error",
            "message": "صلاحية غير كافية, يجب ان تكون سوبر ادمن لتحديث الادمن"
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({
            "status": "error",
            "message": "لا توجد بيانات لتحديثها"
        }), 400

    admin = User.query.filter_by(id=admin_id, role='admin').first()
    if not admin:
        return jsonify({
            "status": "error",
            "message": "الادمن غير موجود"
        }), 404

    if 'username' in data:
        duplicate_admin = User.query.filter_by(username=data['username']).first()
        if duplicate_admin and duplicate_admin.id != admin.id:
            return jsonify({
                "status": "error",
                "message": "اسم المستخدم مسجل مسبقا"
            }), 400
        admin.username = data['username']

    if 'password' in data:
        admin.password_hash = generate_password_hash(data['password'])

    if 'is_active' in data:
        admin.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "تم تحديث الادمن بنجاح"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
