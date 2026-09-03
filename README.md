# Ticket Booking System - Phase 1

#Live Link - https://ticket-booking-service-ailr.onrender.com

## Project Overview
This is a realistic REST API backend for a Ticket Booking System, serving as Phase 1 of a larger project. The backend provides endpoints for users, events, seat listings, bookings, and simulated payments. 

Phase 1 focuses entirely on the Python Flask application and SQLite database structure. 

## Architecture
The application is built using the **Flask Application Factory** pattern and organizes routes logically using **Flask Blueprints**. The system prevents double-bookings using SQL-level updates with WHERE clauses, making it concurrency-safe across multiple instances.

### Technologies
- Python 3
- Flask
- Flask-SQLAlchemy (with SQLite)
- pytest (for testing)

## Project Structure
```
TBS/
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── config.py           # Configuration (Dev/Testing)
│   ├── models/             # Database models
│   ├── routes/             # API blueprints (endpoints)
│   └── utils/              # Helper utilities (logger)
├── tests/                  # pytest suite
├── requirements.txt        # Python dependencies
├── seed.py                 # Database initialization script
├── run.py                  # Entry point
└── README.md               # Documentation
```

## Setup & Installation (Local Development)

### 1. Create a Virtual Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the Database
Run the `seed.py` script to create the initial SQLite database with sample data:
```bash
python seed.py
```
This will generate `tbs.db` with sample users, events, and seats.

### 4. Run the Application
```bash
python run.py
```
The server will start at `http://127.0.0.1:5000/`.

## Docker Deployment (Phase 2)

### Prerequisites
- Docker must be installed and running on your system.

### Build the Docker Image
To package the Flask application into a lightweight Docker image, run:
```bash
docker build -t ticket-booking-app:latest .
```
*(Note: The Dockerfile runs `seed.py` to temporarily initialize an SQLite database inside the image for testing purposes.)*

### Run the Docker Container
Start the container and map port 5000:
```bash
docker run -d -p 5000:5000 --name tbs-container ticket-booking-app:latest
```

### Accessing the API & Health Check
Once running, you can access the Flask API at `http://127.0.0.1:5000`.
To verify the container is healthy, test the `/health` endpoint:
```bash
curl http://127.0.0.1:5000/health
# Expected: {"status": "ok"}
```

### Stop and Remove the Container
```bash
docker stop tbs-container
docker rm tbs-container
```

### Database Evolution Note
Currently, the application uses **SQLite** temporarily to facilitate easy local testing and initial Dockerization. **PostgreSQL will be introduced** as the persistent database solution before moving on to Kubernetes in the next phases.

## API Endpoints

### Health
- `GET /health`: Returns `{"status": "ok"}`. (Intended for future Kubernetes liveness/readiness probes).

### Users
- `POST /api/users`: Creates a user.
- `GET /api/users/<id>`: Retrieves user details.

### Events
- `GET /api/events`: Retrieves all events.
- `GET /api/events/<id>`: Retrieves a specific event.
- `POST /api/events`: Creates an event.

### Seats
- `GET /api/events/<event_id>/seats`: Retrieves all seats for a given event, including availability, category, and price.

### Bookings
- `POST /api/bookings`: Books a seat. Checks for concurrency/double booking. Sets status to `PENDING`.
- `GET /api/bookings/<id>`: Retrieves booking details.
- `DELETE /api/bookings/<id>`: Cancels a booking, marks status as `CANCELLED`, and releases the seat.

### Payments
- `POST /api/payments`: Simulates a payment.
  - Payload: `{"booking_id": 1, "simulate_status": "SUCCESS"}` -> Updates booking to `CONFIRMED`.
  - Payload: `{"booking_id": 1, "simulate_status": "FAILED"}` -> Cancels the booking and releases the seat.

## Testing
To run the automated test suite in an isolated in-memory SQLite database, run:
```bash
pytest tests/
```

## Future Architecture
Phase 1 implements a modular structure that lays the groundwork for the following architecture:
```
Flask Application
       ↓
     Docker
       ↓
   Kubernetes (2 Flask Pods)
       ↓
  Kubernetes Service
       ↓
   Prometheus
       ↓
    Grafana
```
**Note:** Docker, Kubernetes, Prometheus, and Grafana are explicitly *NOT* implemented in Phase 1, but the codebase is structured cleanly to support this pipeline in the future without rewriting the core application.
