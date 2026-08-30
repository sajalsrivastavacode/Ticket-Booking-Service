# Use a lightweight official Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Temporarily initialize SQLite database with sample data
RUN python seed.py

# Expose port 5000
EXPOSE 5000

# Start the application
CMD ["python", "run.py"]
