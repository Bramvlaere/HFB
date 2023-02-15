# Use the official Python image as a base
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt /app

# Install the dependencies listed in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script to the container
COPY main.py /app
COPY config.json /app


# Run the script
CMD [ "python", "./main.py" ]
