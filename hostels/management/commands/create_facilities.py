from django.core.management.base import BaseCommand
from hostels.models import Facility

class Command(BaseCommand):
    help = 'Create default facilities for hostels'

    def handle(self, *args, **options):
        facilities = [
            {'name': 'Wi-Fi', 'icon': 'fas fa-wifi'},
            {'name': 'Air Conditioning', 'icon': 'fas fa-snowflake'},
            {'name': 'Laundry Service', 'icon': 'fas fa-tshirt'},
            {'name': 'Meals Included', 'icon': 'fas fa-utensils'},
            {'name': 'CCTV Security', 'icon': 'fas fa-video'},
            {'name': 'Study Room', 'icon': 'fas fa-book'},
            {'name': 'Parking', 'icon': 'fas fa-car'},
            {'name': 'Generator Backup', 'icon': 'fas fa-bolt'},
            {'name': 'Water Cooler', 'icon': 'fas fa-tint'},
            {'name': 'Common Kitchen', 'icon': 'fas fa-fire'},
            {'name': 'Recreation Area', 'icon': 'fas fa-gamepad'},
            {'name': 'Gym/Fitness', 'icon': 'fas fa-dumbbell'},
            {'name': 'Medical Facility', 'icon': 'fas fa-first-aid'},
            {'name': 'Locker Facility', 'icon': 'fas fa-lock'},
            {'name': 'Transportation', 'icon': 'fas fa-bus'},
            {'name': 'Housekeeping', 'icon': 'fas fa-broom'},
            {'name': 'Cable TV', 'icon': 'fas fa-tv'},
            {'name': 'Balcony/Terrace', 'icon': 'fas fa-building'},
            {'name': 'Garden Area', 'icon': 'fas fa-tree'},
            {'name': '24/7 Water Supply', 'icon': 'fas fa-faucet'},
        ]

        created_count = 0
        for facility_data in facilities:
            facility, created = Facility.objects.get_or_create(
                name=facility_data['name'],
                defaults={'icon': facility_data['icon']}
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created facility: {facility.name}")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} facilities")
        )
