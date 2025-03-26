# Start with a Python base image
FROM python:3.11-slim

# Set environment variables
# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Prevent python from buffering stdout/stderr
ENV PYTHONUNBUFFERED 1
# Point Flask to your run script
ENV FLASK_APP=app.py
# Set a default database URL (can be overridden by Docker Compose)
ENV DATABASE_URL=sqlite:////app/instance/memos.db
# Use absolute path inside container

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for psycopg2, mysqlclient)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install uv
RUN uv pip install --no-cache-dir -r requirements.txt --system

# Create instance folder structure (will be mounted over by volume)
# This ensures paths exist if volume isn't mounted immediately.
RUN mkdir -p /app/instance/uploads

# Copy the rest of the application code
COPY ./src .

# Run database migrations
# This runs during the build process. Alternatively, run it as an entrypoint script.
RUN flask db upgrade

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application using Gunicorn
# Binds to 0.0.0.0 to be accessible from outside the container
# run:app assumes 'app' object is created in run.py by create_app()
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]