# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Add Datadog’s source code integration
ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL} 
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir datadog-api-client requests schedule python-json-logger

# Run fetch_wait_times.py when the container launches
CMD ["python", "./fetch_wait_times.py"]
