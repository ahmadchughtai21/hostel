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

        # Sample hostel data
        sample_hostels = [
            {
                'name': 'FAST University Lodge',
                'address': 'House 123, Block A, Johar Town, Near FAST-NUCES Lahore Campus',
                'description': 'Modern hostel facility specifically designed for FAST University students. Features include high-speed Wi-Fi, study halls, air-conditioned rooms, and 24/7 security. Just 5 minutes walk to campus.',
                'contact_email': 'info@fastlodge.pk',
                'contact_phone': '+923001234567',
                'whatsapp_number': '+923001234567',
                'google_location_link': 'https://maps.google.com/maps?q=31.4697,-74.2728',
                'nearby_landmark': 'FAST-NUCES Lahore',
                'landmark_distance': Decimal('0.3'),
                'is_featured': True,
            },
            {
                'name': 'LUMS Heights Hostel',
                'address': '456 DHA Phase 5, Near LUMS University, Lahore Cantt',
                'description': 'Premium accommodation for LUMS students and faculty. Offers furnished single and shared rooms with modern amenities, common kitchen, gym access, and transport facility to campus.',
                'contact_email': 'contact@lumsheights.pk',
                'contact_phone': '+923009876543',
                'whatsapp_number': '+923009876543',
                'google_location_link': 'https://maps.google.com/maps?q=31.4939,-74.4119',
                'nearby_landmark': 'LUMS University',
                'landmark_distance': Decimal('0.8'),
                'is_featured': False,
            },
            {
                'name': 'UMT Student Residence',
                'address': '789 C-II Block, C-2 Johar Town, Near UMT Campus',
                'description': 'Comfortable and affordable accommodation near University of Management & Technology. Clean rooms, mess facility, study areas, and easy access to public transport.',
                'contact_email': 'info@umtresidence.pk',
                'contact_phone': '+923216549873',
                'whatsapp_number': '+923216549873',
                'google_location_link': 'https://maps.google.com/maps?q=31.4504,-74.3072',
                'nearby_landmark': 'UMT Lahore',
                'landmark_distance': Decimal('0.5'),
                'is_featured': False,
            },
            {
                'name': 'COMSATS Gateway Hostel',
                'address': '321 Park Road, Near COMSATS University Lahore Campus',
                'description': 'State-of-the-art hostel facility for COMSATS students with modern infrastructure, high-speed internet, recreational facilities, and professional management. Safe and secure environment.',
                'contact_email': 'info@comsatsgateway.pk',
                'contact_phone': '+923451122334',
                'whatsapp_number': '+923451122334',
                'google_location_link': 'https://maps.google.com/maps?q=31.4220,-74.4044',
                'nearby_landmark': 'COMSATS University Lahore',
                'landmark_distance': Decimal('0.4'),
                'is_featured': True,
            },
            {
                'name': 'PU Campus Lodge',
                'address': '654 New Campus Road, University Town, Near Punjab University',
                'description': 'Budget-friendly accommodation for Punjab University students. Family-run hostel with home-cooked meals, personal attention, and a supportive academic environment.',
                'contact_email': 'info@pucampus.pk',
                'contact_phone': '+923334455667',
                'whatsapp_number': '+923334455667',
                'google_location_link': 'https://maps.google.com/maps?q=31.5804,-74.3587',
                'nearby_landmark': 'Punjab University',
                'landmark_distance': Decimal('0.6'),
                'is_featured': False,
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
                    'is_featured': hostel_data.get('is_featured', False),
                    'is_verified': random.choice([True, False]),  # Random verification status
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
                            'description': f"Comfortable {room_data['type']} accommodation"
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
