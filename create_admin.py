import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'superpass123')
    print("Суперпользователь успешно создан!")
else:
    user = User.objects.get(username='admin')
    user.set_password('superpass123')
    user.save()
    print("Пароль для пользователя admin успешно перезаписан на superpass123!")