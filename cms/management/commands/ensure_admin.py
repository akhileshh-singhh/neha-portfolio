"""Create the admin login from environment variables (handy on hosts without a shell, e.g. Render free tier).

    DJANGO_SUPERUSER_USERNAME=neha DJANGO_SUPERUSER_PASSWORD=... DJANGO_SUPERUSER_EMAIL=... python manage.py ensure_admin
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser from DJANGO_SUPERUSER_* env vars if it does not exist yet."

    def handle(self, *args, **opts):
        u = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        p = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not (u and p):
            self.stdout.write("DJANGO_SUPERUSER_USERNAME / _PASSWORD not set - skipping.")
            return
        User = get_user_model()
        if User.objects.filter(username=u).exists():
            self.stdout.write(f"Admin user '{u}' already exists.")
            return
        User.objects.create_superuser(u, os.environ.get("DJANGO_SUPERUSER_EMAIL", ""), p)
        self.stdout.write(self.style.SUCCESS(f"Created admin user '{u}'."))
