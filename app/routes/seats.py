from flask import Blueprint, jsonify
from app.models.seat import Seat
from app.models.event import Event

seats_bp = Blueprint('seats', __name__)

@seats_bp.route('/events/<int:event_id>/seats', methods=['GET'])
def get_event_seats(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
        
    seats = Seat.query.filter_by(event_id=event_id).all()
    return jsonify({
        "event_id": event_id,
        "seats": [seat.to_dict() for seat in seats]
    }), 200
