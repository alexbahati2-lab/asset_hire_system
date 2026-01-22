# deploy_setup.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command

# Run migrations
call_command("migrate", interactive=False)

# Read admin credentials from environment
ADMIN_USER = os.environ.get("DJANGO_ADMIN_USER")
ADMIN_EMAIL = os.environ.get("DJANGO_ADMIN_EMAIL")
ADMIN_PASS = os.environ.get("DJANGO_ADMIN_PASSWORD")

if not ADMIN_PASS:
    print("Admin password not set. Skipping superuser creation.")
elif not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username=ADMIN_USER or "admin",
        email=ADMIN_EMAIL or "admin@example.com",
        password=ADMIN_PASS,
    )
    print("Superuser created successfully")
else:
    print("Superuser already exists")
