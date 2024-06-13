
        #!/bin/bash

        # Start Gunicorn
        gunicorn DevOps_Streamline.wsgi:application --bind 0.0.0.0:8000 --workers 3 &

        # Start Nginx
        nginx -g 'daemon off;'
        