# Choose a slim Python base image for a small runtime footprint
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for compiling certain packages if necessary
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to optimize Docker layer caching
COPY api/requirements.txt /app/api/requirements.txt

# Install the Python package dependencies
RUN pip install --no-cache-dir -r /app/api/requirements.txt

# Download and install the spaCy English model required by the /extract endpoint
RUN python -m spacy download en_core_web_sm

# Copy the rest of the api source code into the container
COPY api /app/api

# Expose the FastAPI port
EXPOSE 8000

# Start uvicorn from the repo root to preserve package-relative imports (api.main:app)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]