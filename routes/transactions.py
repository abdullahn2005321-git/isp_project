from flask import Blueprint, request, jsonify
from models import db, Subscriber, Transaction, Area, User
from routes.subscribers import get_current_admin_id
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

transactions_bp = Blueprint('transactions', __name__)


def can_process_transaction():
    user = db.session.get(User, int(get_jwt_identity()))
    role = str(user.role if user else '').strip().lower()
    return role in {'admin', 'editor'}

#==============================
#==========payment endpoints
#==============================
@transactions_bp.route('/api/transactions/payment', methods=['POST'])
@jwt_required()
def add_payment():
    admin_id = get_current_admin_id()
    user_id = get_jwt_identity()

    if not can_process_transaction():
        return jsonify({
            "status": "error",
            "message": "هذه الصلاحية لا تسمح بالتسديد أو التجديد."
        }), 403

    data = request.get_json()

    if not data or not 'subscriber_id' in data or not 'amount' in data:
        return jsonify({
            "status": "error",
            "message": "subscriber_id and amount are required."
        }), 400

    payment_method = data.get('payment_type', 'cash')
    if payment_method not in {'cash', 'electronic'}:
        return jsonify({
            "status": "error",
            "message": "Invalid payment method. Must be 'cash' or 'electronic'."
        }), 400

    sub = Subscriber.query.join(Area).with_for_update().filter(
        Subscriber.id == data['subscriber_id'],
        Area.admin_id == admin_id,
        Subscriber.is_active == True
    ).first()

    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404

    
    try:
        payment_amount = int(data['amount'])
        if payment_amount <= 999:
            raise ValueError("المبلغ يجب ان يكون اكبر من 999 دينار")
    except (ValueError, TypeError, KeyError):
        return jsonify({
            "message": "بيانات خاطئة! يرجى التأكد من إدخال مبلغ صحيح وأكبر من 999 دينار.",
            "status": "error"
        }) , 400

    new_transaction = Transaction(
        subscriber_id = sub.id,
        user_id = user_id,
        transaction_type = 'payment',
        payment_method = payment_method,
        amount = payment_amount
    )

    sub.balance += payment_amount

    if sub.balance >= 0:
        sub.promise_date = None

    try:
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Payment of {payment_amount} added for subscriber '{sub.name}'.",
            "new_balance": sub.balance,
            "payment_date": new_transaction.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

#==============================
#==========renewal endpoints
#==============================
@transactions_bp.route('/api/transactions/renewal', methods=['POST'])
@jwt_required()
def renew_subscription():
    admin_id = get_current_admin_id()
    user_id = get_jwt_identity()

    if not can_process_transaction():
        return jsonify({
            "status": "error",
            "message": "هذه الصلاحية لا تسمح بالتسديد أو التجديد."
        }), 403

    data = request.get_json()
    
    if not data or not 'subscriber_id' in data or not 'amount' in data:
        return jsonify({
            "status": "error",
            "message": "subscriber_id and amount are required."
        }), 400
    
    sub = Subscriber.query.join(Area).with_for_update().filter(
        Subscriber.id == data['subscriber_id'],
        Area.admin_id == admin_id,
        Subscriber.is_active == True
    ).first()

    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404
    
    try:
        renewal_amount = int(data['amount'])
        if renewal_amount <= 999:
            raise ValueError("المبلغ يجب ان يكون اكبر من 999 دينار")
    except (ValueError, TypeError, KeyError):
        return jsonify({
            "message": "بيانات خاطئة! يرجى التأكد من إدخال مبلغ صحيح وأكبر من 999 دينار.",
            "status": "error"
        }) , 400
    
    is_cash = data.get('is_cash', False)

    sub.balance -= renewal_amount
    
    renewal_trans = Transaction(
        subscriber_id=sub.id,
        user_id=user_id,
        transaction_type='renewal',
        amount=renewal_amount
    )
    db.session.add(renewal_trans)

    if is_cash:
        payment_trans = Transaction(
            subscriber_id=sub.id,
            user_id=user_id,
            transaction_type='payment',
            amount=renewal_amount
        )

        sub.balance += renewal_amount

        db.session.add(payment_trans)
        
        if sub.balance >= 0:
            sub.promise_date = None
            
    else:
        promise_date = data.get('promise_date')
        if sub.balance < 0:
            if not promise_date or promise_date.strip() == "":
                return jsonify({
                    "status": "error",
                    "message": "المشترك أصبح مديوناً الآن. يجب تحديد تاريخ (وعد) للتسديد!"
                }), 400
            else:
                sub.promise_date = promise_date
        else:
            sub.promise_date = None

    try:
        db.session.commit()
        msg_type = "نقداً 💵" if is_cash else "بالدين 📝"
        return jsonify({
            "status": "success",
            "message": f"تم تجديد اشتراك '{sub.name}' بنجاح ({msg_type}).",
            "renewal_date": renewal_trans.transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "new_balance": sub.balance
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
