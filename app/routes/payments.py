from flask import Blueprint, request, jsonify
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.seat import Seat
from app import db
import logging

payments_bp = Blueprint('payments', __name__)
logger = logging.getLogger(__name__)

@payments_bp.route('/payments', methods=['POST'])
def create_payment():
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({"error": "Missing booking_id"}), 400
        
    booking_id = data['booking_id']
    simulate_status = data.get('simulate_status', 'SUCCESS').upper()
    
    if simulate_status not in ['SUCCESS', 'FAILED']:
        return jsonify({"error": "Invalid simulate_status"}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
        
    if booking.status != 'PENDING':
        return jsonify({"error": f"Cannot process payment for booking in {booking.status} state"}), 400
        
    # Seat price
    amount = booking.seat.price
        
    payment = Payment(
        booking_id=booking.id,
        amount=amount,
        status=simulate_status
    )
    db.session.add(payment)
    
    if simulate_status == 'SUCCESS':
        booking.status = 'CONFIRMED'
        logger.info(f"Payment successful for booking {booking.id}")
    else:
        # If payment fails, cancel the booking and release the seat
        booking.status = 'CANCELLED'
        booking.seat.is_booked = False
        logger.warning(f"Payment failed for booking {booking.id}, seat released")
        
    db.session.commit()
    return jsonify(payment.to_dict()), 201
