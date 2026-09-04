from flask import Blueprint, request, jsonify
from models import User, db, Subscriber, Transaction, Area, DailyFinancialSummary, get_iraq_now
from routes.subscribers import get_current_admin_id
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from sqlalchemy import extract
from datetime import datetime, timedelta

logging_and_reporting_bp = Blueprint('logging_and_reporting', __name__)

# ==============================
# ====== Monthly Summary Endpoint
# ==============================

@logging_and_reporting_bp.route('/api/monthly-summary', methods=['GET'])
@jwt_required()
def get_monthly_financial_summary():
    """
    جلب ملخص مالي شهري للأدمن الحالي مع إجماليات الشهر.
    المعاملات الاختيارية عبر الـ Query Params:
    - year: السنة (افتراضياً: السنة الحالية بتوقيت العراق)
    - month: الشهر (افتراضياً: الشهر الحالي بتوقيت العراق)
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404

    admin_id = user.id if user.role == 'admin' else user.parent_admin_id
    if not admin_id:
        return jsonify({"error": "لا تملك صلاحية الوصول لهذا التقرير"}), 403

    now = get_iraq_now()
    year = request.args.get('year', default=now.year, type=int)
    month = request.args.get('month', default=now.month, type=int)

    daily_records = DailyFinancialSummary.query.filter(
        DailyFinancialSummary.admin_id == admin_id,
        extract('year', DailyFinancialSummary.summary_date) == year,
        extract('month', DailyFinancialSummary.summary_date) == month
    ).order_by(DailyFinancialSummary.summary_date.asc()).all()

    days_data = []
    for record in daily_records:
        days_data.append({
            "summary_date": record.summary_date.strftime("%Y-%m-%d"),
            "renewals_count": record.renewals_count,
            "total_renewals_amount": record.total_renewals_amount,
            "payments_count": record.payments_count,
            "cash_received": record.cash_received,
            "electronic_received": record.electronic_received,
            "total_collected": record.total_collected,
            "total_transactions_count": record.total_transactions_count
        })

    monthly_totals = {
        "total_renewals_count": sum(d["renewals_count"] for d in days_data),
        "total_renewals_amount": sum(d["total_renewals_amount"] for d in days_data),
        "total_payments_count": sum(d["payments_count"] for d in days_data),
        "total_cash_received": sum(d["cash_received"] for d in days_data),
        "total_electronic_received": sum(d["electronic_received"] for d in days_data),
        "grand_total_collected": sum(d["total_collected"] for d in days_data),
        "total_transactions_count": sum(d["total_transactions_count"] for d in days_data),
        "active_days_count": len(days_data)
    }

    return jsonify({
        "success": True,
        "admin_id": admin_id,
        "year": year,
        "month": month,
        "totals": monthly_totals,
        "days": days_data
    }), 200



#==============================
#==========daily report endpoint
#==============================
@logging_and_reporting_bp.route('/api/daily_report', methods=['GET'])
@jwt_required()
def daily_report():
    try:
        claims = get_jwt()
        user_role = claims.get("role")
        admin_id = get_current_admin_id()

        if user_role != 'admin' and user_role != 'editor':
            return jsonify({
                "status": "error",
                "message": "Unauthorized access. Only admin and editors can view the daily report."
            }), 403

        target_date = request.args.get('date', get_iraq_now().date().isoformat())

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
        user_role = claims.get("role")
        admin_id = get_current_admin_id()

        if user_role != 'admin' and user_role != 'editor':
            return jsonify({
                "status": "error",
                "message": "Unauthorized access. Only admin and editors can view logs."
            }), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        subscriber_id = request.args.get('subscriber_id', type=int)
        start_date_raw = request.args.get('start_date','', type=str).strip()
        end_date_raw = request.args.get('end_date','', type=str).strip()
        renewal = request.args.get('renewal', type=str)
        payment = request.args.get('payment', type=str)

        start_date = None
        end_date = None

        if start_date_raw:
            try:
                start_date = datetime.strptime(start_date_raw, "%Y-%m-%d")
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid start_date format. Use YYYY-MM-DD."
                }), 400

        if end_date_raw:
            try:
                end_date = datetime.strptime(end_date_raw, "%Y-%m-%d")
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid end_date format. Use YYYY-MM-DD."
                }), 400

        if start_date and end_date and start_date > end_date:
            return jsonify({
                "status": "error",
                "message": "start_date cannot be later than end_date."
            }), 400

        if end_date:
            end_date += timedelta(days=1)

        query = Transaction.query.join(Subscriber).join(Area).filter(
            Area.admin_id == admin_id,
        )

        if subscriber_id is not None:
            query = query.filter(Subscriber.id == subscriber_id)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date < end_date)

        if renewal and renewal.strip().lower() in ('1', 'true', 'yes', 'on'):
            query = query.filter(Transaction.transaction_type == 'renewal')
        if payment and payment.strip().lower() in ('1', 'true', 'yes', 'on'):
            query = query.filter(Transaction.transaction_type == 'payment')

        paginated_transactions = query.order_by(
            Transaction.transaction_date.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        transaction = paginated_transactions.items

        logs = []
        for t in transaction:
            t_type_arabic = "تسديد" if t.transaction_type == 'payment' else "تجديد"
            actor_name = t.processed_by.username if t.processed_by else None

            logs.append({
                "type": t_type_arabic,
                "subscriber_id": t.subscriber_id,
                "subscriber_name": t.subscriber.name if t.subscriber else None,
                "processed_by": actor_name,
                "processed_by_name": actor_name,
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