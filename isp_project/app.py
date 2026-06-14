from flask import Flask , request, jsonify
from models import db, Area, Subscriber, Payment, Renewal
from datetime import date
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1/isp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
#==============================
#=============area endpoints
#==============================
@app.route('/api/areas', methods=['POST'])
def add_area():
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({"status": "error", "message": "Area name is required."}), 400
    
    new_area = Area(name=data['name'])

    try:
        db.session.add(new_area)
        db.session.commit()
        return jsonify({"status": "success", "message": "Area added successfully."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/areas', methods=['GET'])
def get_areas():
    try:
        areas = Area.query.all()

        areas_list = [{"id": area.id, "name": area.name} for area in areas]
        return jsonify({
            "status": "success",
            "areas": areas_list
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#==============================
#=======subscriber endpoints
#==============================
@app.route('/api/subscribers', methods=['POST'])
def add_subscriber():
    data = request.get_json()

    required_fields = ['name', 'phone_number', 'area_id']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "message": f"{field} is required."
            }), 400

    new_subscriber = Subscriber(
        name = data['name'],
        phone_number = data['phone_number'],
        area_id = data['area_id'],
        parent_company_id = data.get('parent_company_id', ''),
        balance = float(data.get('balance', 0.0)),
        promise_date = data.get('promise_date') if data.get('promise_date') and data.get('promise_date').strip() != "" else None,
        notes = data.get('notes', '')
    )
    try:
        db.session.add(new_subscriber)
        db.session.commit()
        return jsonify({
            "status" : "success",
            "message": f"Subscriber added successfully'{new_subscriber.name}'.",
            "subscriber_id": new_subscriber.id
        }), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Phone number already exists."
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    try:
        subscribers = Subscriber.query.all()

        sub_list = []
        for subscriber in subscribers:
            sub_list.append({
                "id": subscriber.id,
                "name": subscriber.name,
                "phone_number": subscriber.phone_number,
                "area_id": subscriber.area_id,
                "area_name": subscriber.area.name if subscriber.area else None,
                "parent_company_id": subscriber.parent_company_id,
                "notes": subscriber.notes,
                "balance": subscriber.balance,
                "promise_date": subscriber.promise_date
            })
        
        return jsonify({
            "status": "success",
            "total": len(sub_list),
            "subscribers": sub_list
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/subscribers/<int:sub_id>', methods=['GET'])
def get_subscriber(sub_id):
    sub = Subscriber.query.get(sub_id)
    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404
    
    sub_data = {
        "id": sub.id,
        "name": sub.name,
        "phone": sub.phone_number if sub.phone_number and sub.phone_number.strip() != "" else "لا يوجد رقم مسجل",
        "area_id": sub.area_id,
        "area_name": sub.area.name if sub.area else None,
        "parent_company_id": sub.parent_company_id,
        "notes": sub.notes,
        "balance": sub.balance,
        "promise_date": str(sub.promise_date) if sub.promise_date else "لا يوجد وعد مسجل"
    }
    return jsonify({
        "status": "success",
        "subscriber": sub_data
    }), 200

#==============================
#=========promises endpoints
#==============================
@app.route('/api/promises_today', methods=['GET'])
def get_promises_today():
    try:
        today = str(date.today())
        subscribers = Subscriber.query.filter(db.func.date(Subscriber.promise_date) == today).all()

        subs_list = []
        for sub in subscribers:
            subs_list.append({
                "id": sub.id,
                "name": sub.name,
                "phone": sub.phone_number if sub.phone_number and sub.phone_number.strip() != "" else "لا يوجد رقم مسجل",
                "area_id": sub.area_id,
                "area_name": sub.area.name if sub.area else None,
                "parent_company_id": sub.parent_company_id,
                "notes": sub.notes,
                "balance": sub.balance,
                "promise_date": str(sub.promise_date) if sub.promise_date else "لا يوجد وعد مسجل"
            })
        
        return jsonify({
            "status": "success",
            "count": len(subs_list),
            "subscribers": subs_list
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/subscribers/<int:sub_id>', methods=['PUT'])
def update_subscriber(sub_id):

    sub = Subscriber.query.get(sub_id)
    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404

    data = request.get_json()

    if 'area_id' in data:

        new_area = Area.query.get(data['area_id'])
        if not new_area:
            return jsonify({
                "status": "error",
                "message": "Area not found."
            }), 404
        sub.area_id = data['area_id']
    
    if 'phone_number' in data:
        sub.phone_number = data['phone_number']
    
    if 'name' in data:
        sub.name = data['name']
    
    if 'parent_company_id' in data:
        sub.parent_company_id = data['parent_company_id']
    
    if 'notes' in data:
        sub.notes = data['notes']

    if 'promise_date' in data:
        sub.promise_date = data['promise_date']

    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Subscriber '{sub.name}' updated successfully."
        }), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Phone number already exists."
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/subscribers/<int:sub_id>', methods=['DELETE'])
def delete_subscriber(sub_id):
    sub = Subscriber.query.get(sub_id)
    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404

    try:
        db.session.delete(sub)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Subscriber '{sub.name}' deleted successfully."
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

#==============================
#==========payment endpoints
#==============================
@app.route('/api/payments', methods=['POST'])
def add_payment():
    data = request.get_json()

    if not data or not 'subscriber_id' in data or not 'amount' in data:
        return jsonify({
            "status": "error",
            "message": "subscriber_id and amount are required."
        }), 400
    
    sub = Subscriber.query.get(data['subscriber_id'])

    if not sub:
        return jsonify({
            "status": "error",
            "message": "Subscriber not found."
        }), 404
    
    payment_amount = float(data['amount'])

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
@app.route('/api/renewals', methods=['POST'])
def renew_subscription():
    data = request.get_json()
    
    if not data or not 'subscriber_id' in data or not 'amount' in data:
        return jsonify({
            "status": "error",
            "message": "subscriber_id and amount are required."
        }), 400
    
    sub = Subscriber.query.get(data['subscriber_id'])

    if not sub:
        return jsonify({"status": "error", "message": "Subscriber not found."}), 404
    
    renewal_amount = float(data['amount'])
    
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

#==============================
#==========daily report endpoint
#==============================
@app.route('/api/daily_report', methods=['GET'])
def daily_report():
    try:
        target_date = request.args.get('date', str(date.today()))

        payments = Payment.query.filter(db.func.date(Payment.payment_date) == target_date).all()

        renewals = Renewal.query.filter(db.func.date(Renewal.renewal_date) == target_date).all()

        payments_amount = sum(payment.amount for payment in payments)

        renewals_amount = sum(renewal.amount for renewal in renewals)

        total = payments_amount - renewals_amount

        if total > 0:
            status = "good"
            message = "Today's collections are good."
        elif total < 0:
            status = "bad"
            message = "Today's collections are bad."
        else:
            status = "neutral"
            message = "Today's collections are neutral."

        report_data = {
            "target_date": target_date,
            "status": "success",
            "message": message,
            "summary": {
                "total_payments_collected": payments_amount,
                "payments_count": len(payments),
                "total_renewals_value": renewals_amount,
                "renewals_count": len(renewals),
                "net_total": total,
                "report_status": status
            }
        }    
        
        return jsonify(report_data), 200
    
    except Exception as e:
         return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

#==============================
#==========logs endpoints
#==============================
@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        payments = Payment.query.order_by(Payment.payment_date.desc()).limit(50).all()
        renewals = Renewal.query.order_by(Renewal.renewal_date.desc()).limit(50).all()

        logs = []

        for payment in payments:
            logs.append({
                "type": "تسديد",
                "subscriber_name": payment.subscriber.name if payment.subscriber else None,
                "amount": payment.amount,
                "date": payment.payment_date.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        for renewal in renewals:
            logs.append({
                "type": "تجديد",
                "subscriber_name": renewal.subscriber.name if renewal.subscriber else None,
                "amount": renewal.amount,
                "date": renewal.renewal_date.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        logs.sort(key=lambda x: x['date'], reverse=True)

        return jsonify({
            "status": "success",
            "logs": logs
        }), 200
    
    except Exception as e:
         return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)