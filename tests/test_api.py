import pytest
from app.models.user import User
from app.models.event import Event
from app.models.seat import Seat
from app.models.booking import Booking
from app import db
from datetime import datetime, timezone

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'

def test_create_user(client):
    response = client.post('/api/users', json={
        "username": "testuser",
        "email": "test@example.com"
    })
    assert response.status_code == 201
    assert response.json['username'] == 'testuser'

def test_create_event(client):
    response = client.post('/api/events', json={
        "name": "Test Event",
        "description": "Test Desc",
        "venue": "Test Venue",
        "date": "2026-10-15"
    })
    assert response.status_code == 201
    assert response.json['name'] == 'Test Event'

def test_get_events(client, app):
    with app.app_context():
        event = Event(name="Event 1", venue="Venue 1", date=datetime.now(timezone.utc))
        db.session.add(event)
        db.session.commit()
        
    response = client.get('/api/events')
    assert response.status_code == 200
    assert len(response.json) >= 1

def test_seat_listing(client, app):
    with app.app_context():
        event = Event(name="Event 1", venue="Venue 1", date=datetime.now(timezone.utc))
        db.session.add(event)
        db.session.commit()
        seat = Seat(event_id=event.id, seat_number="A1", category="VIP", price=1000)
        db.session.add(seat)
        db.session.commit()
        event_id = event.id
        
    response = client.get(f'/api/events/{event_id}/seats')
    assert response.status_code == 200
    assert len(response.json['seats']) == 1

def setup_booking_data(app):
    with app.app_context():
        user = User(username="booker", email="booker@example.com")
        event = Event(name="Booking Event", venue="Venue 1", date=datetime.now(timezone.utc))
        db.session.add(user)
        db.session.add(event)
        db.session.commit()
        
        seat = Seat(event_id=event.id, seat_number="A1", category="VIP", price=1000)
        db.session.add(seat)
        db.session.commit()
        
        return user.id, event.id, seat.id

def test_successful_booking(client, app):
    user_id, event_id, seat_id = setup_booking_data(app)
    
    response = client.post('/api/bookings', json={
        "user_id": user_id,
        "event_id": event_id,
        "seat_id": seat_id
    })
    
    assert response.status_code == 201
    assert response.json['status'] == 'PENDING'
    
    with app.app_context():
        seat = Seat.query.get(seat_id)
        assert seat.is_booked is True

def test_double_booking_prevention(client, app):
    user_id, event_id, seat_id = setup_booking_data(app)
    
    # First booking
    res1 = client.post('/api/bookings', json={
        "user_id": user_id,
        "event_id": event_id,
        "seat_id": seat_id
    })
    assert res1.status_code == 201
    
    # Second booking attempt for same seat
    res2 = client.post('/api/bookings', json={
        "user_id": user_id,
        "event_id": event_id,
        "seat_id": seat_id
    })
    assert res2.status_code == 409
    assert "already booked" in res2.json['error']

def test_booking_cancellation(client, app):
    user_id, event_id, seat_id = setup_booking_data(app)
    
    res = client.post('/api/bookings', json={
        "user_id": user_id,
        "event_id": event_id,
        "seat_id": seat_id
    })
    booking_id = res.json['id']
    
    cancel_res = client.delete(f'/api/bookings/{booking_id}')
    assert cancel_res.status_code == 200
    
    with app.app_context():
        booking = Booking.query.get(booking_id)
        seat = Seat.query.get(seat_id)
        assert booking.status == 'CANCELLED'
        assert seat.is_booked is False

def test_successful_payment(client, app):
    user_id, event_id, seat_id = setup_booking_data(app)
    
    res = client.post('/api/bookings', json={
        "user_id": user_id,
        "event_id": event_id,
        "seat_id": seat_id
    })
    booking_id = res.json['id']
    
    pay_res = client.post('/api/payments', json={
        "booking_id": booking_id,
        "simulate_status": "SUCCESS"
    })
    assert pay_res.status_code == 201
    assert pay_res.json['status'] == 'SUCCESS'
    
    with app.app_context():
        booking = Booking.query.get(booking_id)
        assert booking.status == 'CONFIRMED'
        assert booking.seat.is_booked is True

def test_failed_payment(client, app):
    user_id, event_id, seat_id = setup_booking_data(app)
    
    res = client.post('/api/bookings', json={
        "user_id": user_id,
        "event_id": event_id,
        "seat_id": seat_id
    })
    booking_id = res.json['id']
    
    pay_res = client.post('/api/payments', json={
        "booking_id": booking_id,
        "simulate_status": "FAILED"
    })
    assert pay_res.status_code == 201
    assert pay_res.json['status'] == 'FAILED'
    
    with app.app_context():
        booking = Booking.query.get(booking_id)
        assert booking.status == 'CANCELLED'
        assert booking.seat.is_booked is False
