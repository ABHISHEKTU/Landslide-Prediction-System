web: python download_model.py && python manage.py migrate && gunicorn landslide_detection.wsgi:application --bind 0.0.0.0:$PORT
