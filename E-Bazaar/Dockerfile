FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask gunicorn

# Copy app
COPY . .

# Only expose HTTP
EXPOSE 80

# Run with production server
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]
