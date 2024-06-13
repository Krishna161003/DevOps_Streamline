# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    && apt-get clean

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose
    
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

# Set environment variable for Django settings module
ENV DJANGO_SETTINGS_MODULE=DevOps_Streamline.settings

# Start server
CMD ["./start.sh"]
