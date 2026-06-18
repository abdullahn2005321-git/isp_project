from flask import Blueprint,request, jsonify
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == '123456':
        access_token = create_access_token(identity=username)

        return jsonify({
            "status": "succeess",
            "message": "تم تسجيل بنجاح",
            "token": access_token
        }), 200
    
    else:
        return jsonify({
            "status": "error",
            "message": "اسم المستخدم أو كلمة المرور خاطئة"
        }), 401