from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Set up complete demo data for HostelZa including admin user, facilities, and sample hostels'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting HostelZa demo data setup...\n')
        )

        # Step 1: Create admin user
        self.stdout.write('Step 1: Creating admin user...')
        try:
            call_command('create_admin')
            self.stdout.write(
                self.style.SUCCESS('✓ Admin user created successfully\n')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating admin user: {e}\n')
            )

        # Step 2: Create facilities
        self.stdout.write('Step 2: Creating facilities...')
        try:
            call_command('create_facilities')
            self.stdout.write(
                self.style.SUCCESS('✓ Facilities created successfully\n')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating facilities: {e}\n')
            )

        # Step 3: Create featured plans
        self.stdout.write('Step 3: Creating featured plans...')
        try:
            call_command('create_featured_plans')
            self.stdout.write(
                self.style.SUCCESS('✓ Featured plans created successfully\n')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating featured plans: {e}\n')
            )

        # Step 4: Create sample hostels (limit to 3)
        self.stdout.write('Step 4: Creating sample hostels...')
        try:
            call_command('create_sample_data', '--count=3')
            self.stdout.write(
                self.style.SUCCESS('✓ Sample hostels created successfully\n')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating sample hostels: {e}\n')
            )

        # Final success message
        self.stdout.write(
            self.style.SUCCESS('🎉 HostelZa demo data setup completed!\n')
        )

        self.stdout.write('Demo data includes:')
        self.stdout.write('• Admin user: username="hostelza", password="hostelza1234@"')
        self.stdout.write('• 3 sample hostels near PC Hotel, LGS, and UMT')
        self.stdout.write('• Sample owners, facilities, and room types')
        self.stdout.write('• Featured advertising plans')
        self.stdout.write('\nYou can now login to admin panel at: /admin/')
        self.stdout.write('Or start exploring the website!')
