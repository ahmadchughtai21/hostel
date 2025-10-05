from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create an admin user for testing'

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username='testadmin',
            defaults={
                'email': 'admin@test.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Test',
                'last_name': 'Admin'
            }
        )
        admin.set_password('admin123')
        admin.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS('Admin user created successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists!')
            )

        self.stdout.write('Username: testadmin')
        self.stdout.write('Password: admin123')
