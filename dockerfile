# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    && apt-get clean

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Configure Nginx
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./myproject_nginx.conf /etc/nginx/sites-available/default

# Expose port
EXPOSE 80

# Start server
CMD ["./start.sh"]
