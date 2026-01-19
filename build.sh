set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
# --- 4. CREAR SUPERUSUARIO DESDE CERO ---
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='Proyecto').exists() or \
User.objects.create_superuser('Proyecto', 'ricardo@gmail.com', '123')" \
| python manage.py shell