# Use the official lightweight Python 3.10 image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the FastAPI server when the container starts
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]