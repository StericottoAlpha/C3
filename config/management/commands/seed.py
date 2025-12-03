from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from pathlib import Path
import glob


class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user (username: admin, password: admin)'))

        # Load seed data from JSON files
        fixtures_dir = Path(__file__).resolve().parent.parent.parent / 'fixtures'
        if fixtures_dir.exists():
            seed_files = sorted(glob.glob(str(fixtures_dir / 'seed_*.json')))
            for seed_file in seed_files:
                filename = Path(seed_file).name
                self.stdout.write(f'Loading fixture: {filename}')
                try:
                    call_command('loaddata', seed_file, verbosity=0)
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded {filename}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed to load {filename}: {e}'))
        else:
            self.stdout.write(self.style.WARNING(f'Fixtures directory not found: {fixtures_dir}'))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
