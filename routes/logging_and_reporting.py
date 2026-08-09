from flask import Blueprint, request, jsonify
from models import db, Subscriber, Transaction
from datetime import date
from flask_jwt_extended import jwt_required, get_jwt

logging_and_reporting_bp = Blueprint('logging_and_reporting', __name__)

#==============================
#==========daily report endpoint
#==============================
@logging_and_reporting_bp.route('/api/daily_report', methods=['GET'])
@jwt_required()
def daily_report():
    try:
        claims = get_jwt()
        admin_id = claims.get("admin_id")

        target_date = request.args.get('date', str(date.today()))

        transaction = Transaction.query.join(Subscriber).filter(
            db.func.date(Transaction.transaction_date) == target_date,
            Subscriber.admin_id == admin_id
        ).all()

        payments = [t for t in transaction if t.transaction_type == 'payment']
        renewals = [t for t in transaction if t.transaction_type == 'renewal']

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
@logging_and_reporting_bp.route('/api/logs', methods=['GET'])
@jwt_required()
def get_logs():
    try:
        claims = get_jwt()
        admin_id = claims.get("admin_id")

        transaction = Transaction.query.join(Subscriber).filter(
            Subscriber.admin_id == admin_id,
            Transaction.transaction_type == 'payment'
        ).order_by(Transaction.transaction_date.desc()).limit(50).all()


        logs = []
        for t in transaction:

            t_type_arabic = "تسديد" if t.transaction_type == 'payment' else "تجديد"

            logs.append({
                "type": t_type_arabic,
                "subscriber_name": t.subscriber.name if t.subscriber else None,
                "amount": t.amount,
                "date": t.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
            })


        return jsonify({
            "status": "success",
            "logs": logs[:50]
        }), 200
    
    except Exception as e:
         return jsonify({
            "status": "error",
            "message": str(e)
        }), 500