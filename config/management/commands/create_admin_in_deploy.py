import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser from environment variables if it doesn't exist (for deployment)"

    def handle(self, *args, **options):
        User = get_user_model()

        user_id = os.environ.get("DJANGO_SUPERUSER_USER_ID")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        if not user_id or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_USER_ID and DJANGO_SUPERUSER_PASSWORD must be set"
                )
            )
            return

        if User.objects.filter(user_id=user_id).exists():
            self.stdout.write(
                self.style.WARNING(f"Superuser '{user_id}' already exists.")
            )
            return

        User.objects.create_superuser(
            user_id=user_id, email=email, password=password
        )
        self.stdout.write(
            self.style.SUCCESS(f"Superuser '{user_id}' created successfully.")
        )
