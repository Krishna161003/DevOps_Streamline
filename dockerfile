# Stage 1: Build the Python application
FROM python:3.9-alpine as web

# Setting up the work directory
WORKDIR /home/app/

# Preventing python from writing pyc to docker container
ENV PYTHONDONTWRITEBYTECODE 1

# Flushing out python buffer
ENV PYTHONUNBUFFERED 1

# Updating the OS
RUN apt update

RUN apt install docker-compose

# Installing dependencies
RUN apt install python3-dev

# Copying requirement file
COPY ./requirements.txt ./

# Upgrading pip version
RUN pip install --upgrade pip

# Installing dependencies
RUN pip install gunicorn

# Installing dependencies
RUN pip install --no-cache-dir -r ./requirements.txt

# Copying all the files in our project
COPY . .

# Stage 2: Set up Nginx
FROM nginx:1.23-alpine

# Removing default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

# Copying our nginx.conf
COPY nginx.conf /etc/nginx/conf.d/

# Copying static files from the Python build stage
#COPY --from=web /home/app /usr/share/nginx/html

# Exposing the port for Nginx
#EXPOSE 80

# Starting Nginx
#CMD ["nginx", "-g", "daemon off;"]
