from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from hostels.models import Hostel, RoomType, Facility, HostelFacility, HostelImage
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample hostel data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Number of sample hostels to create')

    def handle(self, *args, **options):
        count = options['count']

        # Create sample owners if they don't exist
        owners = []
        for i in range(3):
            username = f'owner{i+1}'
            email = f'owner{i+1}@example.com'

            owner, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'role': 'owner',
                    'first_name': f'Owner',
                    'last_name': f'{i+1}',
                    'phone_number': f'+9230012345{i}0',
                }
            )
            if created:
                owner.set_password('password123')
                owner.save()
                self.stdout.write(f"Created owner: {username}")
            owners.append(owner)

        # Sample hostel data with specific landmarks
        sample_hostels = [
            {
                'name': 'PC Hotel Student Lodge',
                'address': 'House 25, Shah Jamal Road, Near Pearl Continental Hotel, Lahore',
                'description': 'Premium student accommodation located near the famous Pearl Continental Hotel in the heart of Lahore. Features include modern furnished rooms, high-speed Wi-Fi, 24/7 security, AC rooms, and easy access to shopping malls and restaurants. Perfect for students who prefer city center location.',
                'contact_email': 'info@pcstudentlodge.pk',
                'contact_phone': '+923001234567',
                'whatsapp_number': '+923001234567',
                'google_location_link': 'https://maps.google.com/maps?q=31.5497,-74.3436',
                'nearby_landmark': 'Pearl Continental (PC) Hotel',
                'landmark_distance': Decimal('0.2'),
                'gender_type': 'mixed',
                'is_featured': True,
            },
            {
                'name': 'LGS Campus Hostel',
                'address': '123 Main Boulevard, Near Lahore Grammar School, Gulberg, Lahore',
                'description': 'Comfortable and safe hostel facility near the prestigious Lahore Grammar School. Offers clean rooms, study areas, mess facility with home-cooked meals, and a peaceful environment for studies. Popular among students attending nearby educational institutions.',
                'contact_email': 'contact@lgscampus.pk',
                'contact_phone': '+923009876543',
                'whatsapp_number': '+923009876543',
                'google_location_link': 'https://maps.google.com/maps?q=31.5080,-74.3436',
                'nearby_landmark': 'Lahore Grammar School (LGS)',
                'landmark_distance': Decimal('0.3'),
                'gender_type': 'male',
                'is_featured': False,
            },
            {
                'name': 'UMT Student Residence',
                'address': '456 C-II Block, Johar Town, Near University of Management and Technology',
                'description': 'Modern student accommodation specially designed for UMT students and other university students. Features include spacious rooms, common kitchen, study halls, gym access, high-speed internet, and transport facility. Well-maintained and professionally managed facility.',
                'contact_email': 'info@umtresidence.pk',
                'contact_phone': '+923216549873',
                'whatsapp_number': '+923216549873',
                'google_location_link': 'https://maps.google.com/maps?q=31.4504,-74.3072',
                'nearby_landmark': 'University of Management and Technology (UMT)',
                'landmark_distance': Decimal('0.4'),
                'gender_type': 'female',
                'is_featured': True,
            }
        ]

        created_count = 0
        for i in range(min(count, len(sample_hostels))):
            hostel_data = sample_hostels[i]
            owner = owners[i % len(owners)]

            hostel, created = Hostel.objects.get_or_create(
                name=hostel_data['name'],
                defaults={
                    'owner': owner,
                    'address': hostel_data['address'],
                    'description': hostel_data['description'],
                    'contact_email': hostel_data['contact_email'],
                    'contact_phone': hostel_data['contact_phone'],
                    'whatsapp_number': hostel_data['whatsapp_number'],
                    'google_location_link': hostel_data.get('google_location_link', ''),
                    'nearby_landmark': hostel_data.get('nearby_landmark', ''),
                    'landmark_distance': hostel_data.get('landmark_distance'),
                    'gender_type': hostel_data.get('gender_type', 'mixed'),
                    'is_featured': hostel_data.get('is_featured', False),
                    'is_verified': True,  # All demo hostels are verified
                    'latitude': Decimal('31.5204'),  # Lahore coordinates
                    'longitude': Decimal('74.3587'),
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f"Created hostel: {hostel.name}")

                # Add room types (Pakistani pricing)
                room_types = [
                    {'type': 'single', 'price': random.randint(15000, 25000), 'available_rooms': random.randint(5, 15)},
                    {'type': 'double', 'price': random.randint(10000, 18000), 'available_rooms': random.randint(10, 25)},
                    {'type': 'shared', 'price': random.randint(6000, 12000), 'available_rooms': random.randint(15, 30)},
                ]

                for room_data in room_types:
                    RoomType.objects.get_or_create(
                        hostel=hostel,
                        type=room_data['type'],
                        defaults={
                            'price': Decimal(str(room_data['price'])),
                            'available_rooms': room_data['available_rooms'],
                            'description': f"Comfortable {room_data['type']} room with modern amenities and facilities"
                        }
                    )

                # Add random facilities
                facilities = list(Facility.objects.all())
                selected_facilities = random.sample(facilities, min(len(facilities), random.randint(5, 12)))

                for facility in selected_facilities:
                    HostelFacility.objects.get_or_create(
                        hostel=hostel,
                        facility=facility
                    )

                # Create placeholder images
                # Note: In a real environment, you would upload actual images
                # For now, we'll create image records that will show placeholders
                image_captions = [
                    'Front view of the hostel',
                    'Common room area',
                    'Sample bedroom',
                    'Kitchen facilities'
                ]

                for i, caption in enumerate(image_captions):
                    HostelImage.objects.get_or_create(
                        hostel=hostel,
                        caption=caption,
                        defaults={
                            'is_primary': i == 0,  # First image is primary
                            'image': f'hostel_images/placeholder_{i+1}.jpg'  # Placeholder path
                        }
                    )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} sample hostels")
        )
