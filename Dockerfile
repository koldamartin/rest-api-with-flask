# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port that your application is running on
EXPOSE 5000

# Set the command to run your application
CMD ["python", "app.py"]

# Set the command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]