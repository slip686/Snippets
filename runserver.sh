python manage.py collectstatic
python manage.py migrate
gunicorn snippets.wsgi --bind=0.0.0.0:5000