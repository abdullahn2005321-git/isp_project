from app import app
from models import db, Subscriber, Area
from faker import Faker
import random

fake = Faker('ar_AA')

def seed_subscribers(count=99000):
    with app.app_context():

        areas = Area.query.all()
        if not areas:
            print("❌ يجب إضافة مناطق (Areas) أولاً قبل إضافة المشتركين!")
            return

        print(f"🚀 جاري إضافة {count} مشترك وهمي...")
        
        for i in range(count):
            subscriber = Subscriber(
                name=fake.name(),
                phone_number=fake.phone_number(),
                area_id=random.choice(areas).id,
                admin_id=1,
                balance=random.uniform(-50000, 20000),
                notes="مشترك وهمي للاختبار",
                is_active=True
            )
            db.session.add(subscriber)
            
            
            if i % 100 == 0:
                db.session.commit()
                print(f"✅ تم إضافة {i} مشترك...")

        db.session.commit()
        print(f"🎉 تم إضافة {count} مشترك بنجاح!")

if __name__ == '__main__':
    seed_subscribers()