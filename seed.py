from app import create_app, db
from app.models.user import User
from app.models.event import Event
from app.models.seat import Seat
from datetime import datetime, timezone, timedelta

app = create_app('development')

def seed_data():
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()

        print("Creating users...")
        users = [
            User(username="ashish", email="ashish@example.com"),
            User(username="rahul", email="rahul@example.com"),
            User(username="priya", email="priya@example.com")
        ]
        db.session.add_all(users)
        db.session.commit()

        print("Creating events...")
        event1 = Event(
            name="Rock Concert 2026",
            description="Live music event",
            venue="Delhi Arena",
            date=datetime.now(timezone.utc) + timedelta(days=30)
        )
        event2 = Event(
            name="Comedy Night",
            description="Standup comedy show",
            venue="Mumbai Comedy Club",
            date=datetime.now(timezone.utc) + timedelta(days=15)
        )
        event3 = Event(
            name="Tech Conference 2026",
            description="Annual tech gathering",
            venue="Bangalore Convention Center",
            date=datetime.now(timezone.utc) + timedelta(days=60)
        )
        events = [event1, event2, event3]
        db.session.add_all(events)
        db.session.commit()

        print("Creating seats...")
        categories = [
            ("A1", "VIP", 2500), ("A2", "VIP", 2500),
            ("B1", "PREMIUM", 1500), ("B2", "PREMIUM", 1500),
            ("C1", "REGULAR", 800), ("C2", "REGULAR", 800)
        ]
        
        for event in events:
            for seat_num, cat, price in categories:
                seat = Seat(
                    event_id=event.id,
                    seat_number=seat_num,
                    category=cat,
                    price=price
                )
                db.session.add(seat)
                
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
