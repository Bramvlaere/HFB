# Use the official Python image as a base
FROM python:3.9.7

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt /app

# Install the dependencies listed in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script and config file to the container
COPY main.py /app
COPY config.json /app

# Expose port 8080
EXPOSE 8080

# Run the script using the $PORT environment variable
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
