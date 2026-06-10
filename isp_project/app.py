from flask import Flask , request, jsonify
from models import db, Area, Subscriber, Payment, Renewal
from datetime import date

app = Flask(__name__)
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
            return jsonify({"status": "error", "message": f"{field} is required."}), 400

    new_subscriber = Subscriber(
        name = data['name'],
        phone_number = data['phone_number'],
        area_id = data['area_id'],
        parent_company_id = data.get('parent_company_id', ''),
        notes = data.get('notes', '')
    )
    try:
        db.session.add(new_subscriber)
        db.session.commit()
        return jsonify({
            "status" : "success",
            "message": f"Subscriber added successfully'{new_subscriber.name}'."
        }), 201
    except Exception as e:
        db.session.rollback()
        if 'phone_number' in str(e).lower() or 'duplicate' in str(e).lower():
            return jsonify({
                "status": "error",
                "message": "Phone number already exists."
            }), 400
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
                "parent_company_id": subscriber.parent_company_id,
                "notes": subscriber.notes
            })
        
        return jsonify({
            "status": "success",
            "total": len(sub_list),
            "subscribers": sub_list
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

    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Subscriber '{sub.name}' updated successfully."
        }), 200
    except Exception as e:
        db.session.rollback()

        if 'phone_number' in str(e).lower() or 'duplicate' in str(e).lower():
            return jsonify({
                "status": "error",
                "message": "Phone number already exists."
            }), 400

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
@app.route('/api/renew', methods=['POST'])
def renew_subscription():
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
    
    renewal_amount = float(data['amount'])

    sub.balance -= renewal_amount

    new_renewal = Renewal(
        subscriber_id = sub.id,
        amount = renewal_amount
    )
    try:
        db.session.add(new_renewal)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Subscription renewed for subscriber '{sub.name}' with amount {renewal_amount}.",
            "new_balance": sub.balance,
            "renewal_date": new_renewal.renewal_date.strftime("%Y-%m-%d %H:%M:%S")
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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

if __name__ == '__main__':
    app.run(debug=True)