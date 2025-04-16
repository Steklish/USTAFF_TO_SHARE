# Use the latest Python base image
FROM python:3.11-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .
EXPOSE 5000

# Command to run when the container starts
CMD ["python", "main.py"]
