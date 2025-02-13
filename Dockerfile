# Use an official lightweight Python image.
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Expose a port if needed (e.g., for a web interface; adjust if necessary)
EXPOSE 8000

# Set the default command to run a Python module (adjust as necessary)
CMD ["python", "-m", "src.streamer"]
