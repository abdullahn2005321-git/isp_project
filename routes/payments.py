from flask import Blueprint, request, jsonify
from models import db, Subscriber, Payment, Renewal
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

payments_bp = Blueprint('payments', __name__)

#==============================
#==========payment endpoints
#==============================
@payments_bp.route('/api/payments', methods=['POST'])
@jwt_required()
def add_payment():
    claims = get_jwt()
    admin_id = claims.get("admin_id")

    data = request.get_json()

    if not data or not 'subscriber_id' in data or not 'amount' in data:
        return jsonify({
            "status": "error",
            "message": "subscriber_id and amount are required."
        }), 400
    
    sub = Subscriber.query.with_for_update().filter_by(
        id=data['subscriber_id'],
        admin_id=admin_id,
        is_active=True
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

    new_payment = Payment(
        subscriber_id = sub.id,
        amount = payment_amount
    )

    sub.balance += payment_amount

    if sub.balance >= 0:
        sub.promise_date = None

    try:
        db.session.add(new_payment)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Payment of {payment_amount} added for subscriber '{sub.name}'.",
            "new_balance": sub.balance,
            "payment_date": new_payment.payment_date.strftime("%Y-%m-%d %H:%M:%S")
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
@payments_bp.route('/api/renewals', methods=['POST'])
@jwt_required()
def renew_subscription():
    claims = get_jwt()
    admin_id = claims.get("admin_id")

    data = request.get_json()
    
    if not data or not 'subscriber_id' in data or not 'amount' in data:
        return jsonify({
            "status": "error",
            "message": "subscriber_id and amount are required."
        }), 400
    
    sub = Subscriber.query.with_for_update().filter_by(
        id=data['subscriber_id'],
        admin_id=admin_id,
        is_active=True
    ).first()

    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404
    
    try:
        renewal_amount = float(data['amount'])
        if renewal_amount <= 999:
            raise ValueError("المبلغ يجب ان يكون اكبر من 999 دينار")
    except (ValueError, TypeError, KeyError):
        return jsonify({
            "message": "بيانات خاطئة! يرجى التأكد من إدخال مبلغ صحيح وأكبر من 999 دينار.",
            "status": "error"
        }) , 400
    
    is_cash = data.get('is_cash', False)

    sub.balance -= renewal_amount
    
    new_renewal = Renewal(subscriber_id=sub.id, amount=renewal_amount)
    db.session.add(new_renewal)

    if is_cash:
        new_payment = Payment(subscriber_id=sub.id, amount=renewal_amount)
        db.session.add(new_payment)
        
        sub.balance += renewal_amount
        
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
            "new_balance": sub.balance
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
