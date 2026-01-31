# Use slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire source code
COPY . .

# Expose port (FastAPI default)
EXPOSE 8000

# Run with uvicorn (production-ready with --workers)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]