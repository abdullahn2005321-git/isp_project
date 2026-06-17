from flask import Blueprint, request, jsonify
from models import db, Payment, Renewal
from datetime import date

logging_and_reporting_bp = Blueprint('logging_and_reporting', __name__)

#==============================
#==========daily report endpoint
#==============================
@logging_and_reporting_bp.route('/api/daily_report', methods=['GET'])
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
@logging_and_reporting_bp.route('/api/logs', methods=['GET'])
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