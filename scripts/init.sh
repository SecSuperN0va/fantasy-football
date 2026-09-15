DJANGO_SUPERUSER_PASSWORD=password
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=''

python manage.py makemigrations && python manage.py migrate && python manage.py createsuperuser --noinput

