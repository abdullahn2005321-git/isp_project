from flask import Blueprint, request, jsonify
from models import db, Subscriber, Transaction, Area
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

        transaction = Transaction.query.join(Subscriber).join(Area).filter(
            db.func.date(Transaction.transaction_date) == target_date,
            Area.admin_id == admin_id
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

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        subscriber_id = request.args.get('subscriber_id', type=int)

        query = Transaction.query.join(Subscriber).join(Area).filter(
            Area.admin_id == admin_id,
        )

        if subscriber_id is not None:
            query = query.filter(Subscriber.id == subscriber_id)

        paginated_transactions = query.order_by(
            Transaction.transaction_date.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        transaction = paginated_transactions.items

        logs = []
        for t in transaction:
            t_type_arabic = "تسديد" if t.transaction_type == 'payment' else "تجديد"

            logs.append({
                "type": t_type_arabic,
                "subscriber_id": t.subscriber_id,
                "subscriber_name": t.subscriber.name if t.subscriber else None,
                "amount": t.amount,
                "date": t.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
            })

        return jsonify({
            "status": "success",
            "subscriber_id": subscriber_id,
            "logs": logs,
            "pagination": {
                "current_page": paginated_transactions.page,
                "per_page": paginated_transactions.per_page,
                "total_items": paginated_transactions.total,
                "total_pages": paginated_transactions.pages,
                "has_next": paginated_transactions.has_next,
                "has_prev": paginated_transactions.has_prev
            }
        }), 200
    
    except Exception as e:
         return jsonify({
            "status": "error",
            "message": str(e)
        }), 500