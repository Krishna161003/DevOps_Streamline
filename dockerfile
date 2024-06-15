# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y \
    apache2 \
    curl \
    docker-compose \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Create a volume for Apache configuration
VOLUME /usr/local/apache2/conf

COPY httpd.conf /usr/local/apache2/conf/httpd.conf

# Expose port 80 for Apache
EXPOSE 80

# Run a command to start Apache when the container starts
CMD ["apache2ctl", "-D", "FOREGROUND"]
