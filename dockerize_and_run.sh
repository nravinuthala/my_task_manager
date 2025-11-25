#!/usr/bin/env bash

# dockerize_and_run.sh
# Creates a temporary directory, generates a Dockerfile, copies the app files,
# builds a Docker image and runs a container that serves the FastAPI app.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR"

TMPDIR=$(mktemp -d)
CONTAINER_NAME="taskapp_$(date +%s)"
IMAGE_NAME="taskapp:local"

cleanup() {
  echo "Cleaning up..."
  # Remove temporary directory
  if [[ -n "${TMPDIR:-}" && -d "$TMPDIR" ]]; then
    rm -rf "$TMPDIR"
  fi
}
trap cleanup EXIT

echo "Using temporary build dir: $TMPDIR"

# Create Dockerfile
cat > "$TMPDIR/Dockerfile" <<'DOCKERFILE'
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Avoid generating .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install OS deps required for common Python wheels (kept minimal).
# Some slim images include apt hooks that fail during 'apt-get update' on
# a few platforms; disable APT::Update::Post-Invoke to avoid the error.
RUN apt-get -o APT::Update::Post-Invoke::=/bin/true update \
  && apt-get install -y --no-install-recommends ca-certificates gcc libffi-dev build-essential \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r /app/requirements.txt

# Copy application
COPY . /app

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "myapp:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE

# Copy necessary files into temporary dir
# We copy the top-level files needed for the app
cp "$APP_DIR/myapp.py" "$TMPDIR/" || { echo "ERROR: myapp.py not found in $APP_DIR"; exit 1; }
cp "$APP_DIR/requirements.txt" "$TMPDIR/" || echo "Warning: requirements.txt not found; build may fail"

# Optionally copy other files if present (not required)
# cp "$APP_DIR/test_api.py" "$TMPDIR/" || true

# Build Docker image
echo "Building Docker image $IMAGE_NAME from $TMPDIR"
docker build -t "$IMAGE_NAME" "$TMPDIR"

# If a container with same name exists, remove it
if docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
  echo "Removing existing container $CONTAINER_NAME"
  docker rm -f "$CONTAINER_NAME" || true
fi

# Run container
echo "Running container $CONTAINER_NAME (mapping host:8000 -> container:8000)"
docker run -d --name "$CONTAINER_NAME" -p 8000:8000 "$IMAGE_NAME"

# Wait for the app to be healthy (simple retry loop)
MAX_RETRIES=15
SLEEP_SECONDS=1
RETRY=0
until curl -sSf http://127.0.0.1:8000/ > /dev/null 2>&1; do
  RETRY=$((RETRY+1))
  if [[ $RETRY -ge $MAX_RETRIES ]]; then
    echo "Application did not become healthy after $((MAX_RETRIES*SLEEP_SECONDS))s. Check container logs with: docker logs $CONTAINER_NAME"
    exit 2
  fi
  printf "."
  sleep $SLEEP_SECONDS
done

echo "\nApplication is up and running at http://127.0.0.1:8000/"

echo "To stop the container: docker rm -f $CONTAINER_NAME"

# Keep script running until user quits (optional). Comment out to exit after success.
# echo "Press Ctrl+C to stop and remove the container"
# wait

exit 0
