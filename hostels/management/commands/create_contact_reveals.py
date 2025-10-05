from django.core.management.base import BaseCommand
from hostels.models import ContactReveal, Hostel, User
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create sample contact reveals for testing'

    def handle(self, *args, **options):
        # Get some students and hostels
        students = User.objects.filter(role='student')[:3]
        hostels = Hostel.objects.all()[:3]

        created_count = 0
        for student in students:
            for hostel in hostels[:2]:  # Each student requests 2 hostels
                reveal, created = ContactReveal.objects.get_or_create(
                    user=student,
                    hostel=hostel,
                    defaults={
                        'timestamp': timezone.now(),
                        'ip_address': '127.0.0.1'
                    }
                )
                if created:
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} contact reveal requests!')
        )
