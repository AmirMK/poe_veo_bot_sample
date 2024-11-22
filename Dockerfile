# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements and application files
COPY requirements.txt /app/
COPY app.py /app/
COPY veo_calls.py /app/

# Install the required Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Set the environment variable for port
ENV PORT=8080

# Run the application using Uvicorn (ASGI server for FastAPI)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
