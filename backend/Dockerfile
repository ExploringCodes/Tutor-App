FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY app/ ./app/


# Expose the port (Cloud Run uses PORT env variable, default 8080)
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]