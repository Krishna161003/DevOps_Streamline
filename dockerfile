# Stage 1: Build the Django application
FROM python:3.9-slim AS django

# Setting up the work directory
WORKDIR /home/app/DevOps_Streamline/

# Preventing python from writing pyc to docker container
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update the package list and install required packages
RUN apt update && apt install -y python3-pip

# Copying requirement file
COPY requirements.txt ./

# Upgrading pip version
RUN pip install --upgrade pip

# Installing dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Installing gunicorn
RUN pip install gunicorn

# Copying all the files in our project
COPY . .
