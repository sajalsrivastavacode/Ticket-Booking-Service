from flask import Blueprint, request, jsonify
from app.models.event import Event
from app import db
from datetime import datetime

events_bp = Blueprint('events', __name__)

@events_bp.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events]), 200

@events_bp.route('/events/<int:id>', methods=['GET'])
def get_event(id):
    event = Event.query.get(id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event.to_dict()), 200

@events_bp.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    if not data or not 'name' in data or not 'venue' in data or not 'date' in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        event_date = datetime.strptime(data['date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    event = Event(
        name=data['name'],
        description=data.get('description', ''),
        venue=data['venue'],
        date=event_date
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201
