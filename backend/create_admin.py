import os
import django

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('USERNAME')
email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created successfully!")
else:
    print(f"Superuser {username} already exists.")