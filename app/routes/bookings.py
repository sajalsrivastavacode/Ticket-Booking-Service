from flask import Blueprint, request, jsonify
from app.models.booking import Booking
from app.models.seat import Seat
from app.models.user import User
from app.models.event import Event
from app import db
import logging

bookings_bp = Blueprint('bookings', __name__)
logger = logging.getLogger(__name__)

@bookings_bp.route('/bookings', methods=['GET'])
def get_bookings():
    user_id = request.args.get('user_id', type=int)
    if user_id:
        bookings = Booking.query.filter_by(user_id=user_id).all()
    else:
        bookings = Booking.query.all()
        
    result = []
    for booking in bookings:
        b_dict = booking.to_dict()
        b_dict['event'] = booking.event.to_dict()
        b_dict['seat'] = booking.seat.to_dict()
        result.append(b_dict)
    return jsonify(result), 200

@bookings_bp.route('/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    if not data or 'user_id' not in data or 'event_id' not in data or 'seat_id' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    user_id = data['user_id']
    event_id = data['event_id']
    seat_id = data['seat_id']

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
        
    seat = Seat.query.get(seat_id)
    if not seat:
        return jsonify({"error": "Seat not found"}), 404
        
    if seat.event_id != event_id:
        return jsonify({"error": "Seat does not belong to the requested event"}), 400

    # Concurrency protection: Update only if is_booked is False
    updated_count = db.session.query(Seat).filter(
        Seat.id == seat_id,
        Seat.is_booked == False
    ).update({'is_booked': True})
    
    if updated_count == 0:
        logger.warning(f"Booking conflict for seat {seat_id}")
        db.session.rollback()
        return jsonify({"error": "Seat is already booked"}), 409

    # Create the booking with status PENDING
    booking = Booking(
        user_id=user_id,
        event_id=event_id,
        seat_id=seat_id,
        status='PENDING'
    )
    db.session.add(booking)
    db.session.commit()
    
    logger.info(f"Booking {booking.id} created successfully for seat {seat_id}")
    return jsonify(booking.to_dict()), 201

@bookings_bp.route('/bookings/<int:id>', methods=['GET'])
def get_booking(id):
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    result = booking.to_dict()
    result['user'] = booking.user.to_dict()
    result['event'] = booking.event.to_dict()
    result['seat'] = booking.seat.to_dict()
    if booking.payment:
        result['payment'] = booking.payment.to_dict()
        
    return jsonify(result), 200

@bookings_bp.route('/bookings/<int:id>', methods=['DELETE'])
def cancel_booking(id):
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
        
    if booking.status == 'CANCELLED':
        return jsonify({"error": "Booking is already cancelled"}), 400
        
    # Cancel the booking
    booking.status = 'CANCELLED'
    
    # Release the seat
    seat = Seat.query.get(booking.seat_id)
    if seat:
        seat.is_booked = False
        
    db.session.commit()
    logger.info(f"Booking {id} cancelled and seat {seat.id} released")
    return jsonify({"message": "Booking cancelled successfully"}), 200
