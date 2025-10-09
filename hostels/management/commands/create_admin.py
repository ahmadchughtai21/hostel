from django.core.management.base import BaseCommandfrom django.core.manage        if created:

from django.contrib.auth import get_user_model            self.stdout.write(

                self.style.SUCCESS('Admin user created successfully!')

User = get_user_model()            )

        else:

class Command(BaseCommand):            self.stdout.write(

    help = 'Create an admin user for HostelZa platform'                self.style.WARNING('Admin user already exists!')

            )

    def handle(self, *args, **options):

        admin, created = User.objects.get_or_create(        self.stdout.write(f'Username: {admin.username}')

            username='hostelza',        self.stdout.write(f'Password: hostelza1234@')mport BaseCommand

            defaults={from django.contrib.auth import get_user_model

                'email': 'admin@hostelza.com',

                'role': 'admin',User = get_user_model()

                'is_staff': True,

                'is_superuser': True,class Command(BaseCommand):

                'first_name': 'HostelZa',    help = 'Create an admin user for HostelZa platform'

                'last_name': 'Admin'

            }    def handle(self, *args, **options):

        )        admin, created = User.objects.get_or_create(

        admin.set_password('hostelza1234@')            username='hostelza',

        admin.save()            defaults={

                'email': 'admin@hostelza.com',

        if created:                'role': 'admin',

            self.stdout.write(                'is_staff': True,

                self.style.SUCCESS('Admin user created successfully!')                'is_superuser': True,

            )                'first_name': 'HostelZa',

        else:                'last_name': 'Admin'

            self.stdout.write(            }

                self.style.WARNING('Admin user already exists!')        )

            )        admin.set_password('hostelza1234@')

        admin.save()

        self.stdout.write(f'Username: {admin.username}')

        self.stdout.write(f'Password: hostelza1234@')        if created:
            self.stdout.write(
                self.style.SUCCESS('Admin user created successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists!')
            )

        self.stdout.write('Username: testadmin')
        self.stdout.write('Password: admin123')
