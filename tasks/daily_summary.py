from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import func, case

from models import db, Area, Subscriber, Transaction, DailyFinancialSummary, get_iraq_now

from app import app 

def generate_multi_admin_daily_summary(target_date=None):
    """تلخيص مالي يومي لكل أدمن على حدة"""
    if target_date is None:
        target_date = (get_iraq_now() - timedelta(days=1)).date()

    start_of_day = datetime.combine(target_date, datetime.min.time(), tzinfo=ZoneInfo("Asia/Baghdad"))
    end_of_day = datetime.combine(target_date, datetime.max.time(), tzinfo=ZoneInfo("Asia/Baghdad"))

    try:
        results = db.session.query(
            Area.admin_id.label('admin_id'),
            func.count(case((Transaction.transaction_type == 'renewal', Transaction.id))).label('renewals_count'),
            func.coalesce(func.sum(case((Transaction.transaction_type == 'renewal', Transaction.amount), else_=0)), 0).label('total_renewals_amount'),
            func.count(case((Transaction.transaction_type == 'payment', Transaction.id))).label('payments_count'),
            func.coalesce(func.sum(case(((Transaction.transaction_type == 'payment') & (Transaction.payment_method == 'cash'), Transaction.amount), else_=0)), 0).label('cash_received'),
            func.coalesce(func.sum(case(((Transaction.transaction_type == 'payment') & (Transaction.payment_method == 'electronic'), Transaction.amount), else_=0)), 0).label('electronic_received'),
            func.count(Transaction.id).label('total_transactions_count')
        ).join(
            Subscriber, Transaction.subscriber_id == Subscriber.id
        ).join(
            Area, Subscriber.area_id == Area.id
        ).filter(
            Transaction.transaction_date >= start_of_day,
            Transaction.transaction_date <= end_of_day,
            Transaction.is_active == True
        ).group_by(
            Area.admin_id
        ).all()

        for row in results:
            admin_id = row.admin_id
            cash = int(row.cash_received or 0)
            electronic = int(row.electronic_received or 0)
            total_collected = cash + electronic

            summary = DailyFinancialSummary.query.filter_by(
                summary_date=target_date,
                admin_id=admin_id
            ).first()

            if not summary:
                summary = DailyFinancialSummary(summary_date=target_date, admin_id=admin_id)
                db.session.add(summary)

            summary.renewals_count = int(row.renewals_count or 0)
            summary.total_renewals_amount = int(row.total_renewals_amount or 0)
            summary.payments_count = int(row.payments_count or 0)
            summary.cash_received = cash
            summary.electronic_received = electronic
            summary.total_collected = total_collected
            summary.total_transactions_count = int(row.total_transactions_count or 0)

        db.session.commit()
        print(f"[{get_iraq_now()}] تم بنجاح إنشاء الملخص المالي لجميع المدراء ليوم: {target_date}")

    except Exception as e:
        db.session.rollback()
        print(f"[{get_iraq_now()}] حدث خطأ أثناء إنشاء الملخص المالي: {e}")
        raise e


if __name__ == '__main__':
     with app.app_context():
        generate_multi_admin_daily_summary()