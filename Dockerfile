# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir datadog-api-client requests schedule ddtrace

# Run fetch_wait_times.py when the container launches
CMD ["ddtrace-run", "python", "./fetch_wait_times.py"]
