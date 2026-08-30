from app import db

class Seat(db.Model):
    __tablename__ = 'seats'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    seat_number = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_booked = db.Column(db.Boolean, default=False, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('event_id', 'seat_number', name='uix_event_seat'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'seat_number': self.seat_number,
            'category': self.category,
            'price': self.price,
            'is_booked': self.is_booked
        }
