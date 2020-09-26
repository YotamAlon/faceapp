python -m pip install -r requirements.txt
python manage.py makemigrations faceapp
python manage.py migrate
python manage.py runserver