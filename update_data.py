from hostels.models import Hostel, HostelSubscription
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

# Sample landmarks
landmarks = [
    ('Harvard University', 0.8),
    ('MIT', 1.2),
    ('Stanford University', 0.5),
    ('UC Berkeley', 1.5),
    ('Tech Hub Downtown', 2.0),
    ('Business District Center', 1.8),
    ('Community College', 0.3),
    ('Medical Center', 1.0),
]

google_maps_links = [
    'https://maps.google.com/maps?q=37.7749,-122.4194',
    'https://maps.google.com/maps?q=40.7128,-74.0060',
    'https://maps.google.com/maps?q=34.0522,-118.2437',
]

hostels = Hostel.objects.all()
updated_count = 0

for i, hostel in enumerate(hostels):
    # Add landmark info to most hostels
    if random.random() < 0.8:
        landmark, distance = random.choice(landmarks)
        hostel.nearby_landmark = landmark
        hostel.landmark_distance = Decimal(str(distance))

    # Add Google Maps link to some hostels
    if random.random() < 0.6:
        hostel.google_location_link = random.choice(google_maps_links)

    # Make every 5th hostel featured
    if i % 5 == 0:
        hostel.is_featured = True

    hostel.save()
    updated_count += 1
    print(f'Updated {hostel.name} - Featured: {hostel.is_featured}, Landmark: {hostel.nearby_landmark}')

# Create subscriptions for hostels that don't have them
for hostel in hostels:
    subscription, created = HostelSubscription.objects.get_or_create(
        hostel=hostel,
        defaults={
            'monthly_fee': Decimal('29.99'),
            'status': 'active' if hostel.is_verified else 'pending',
            'subscription_start_date': timezone.now().date() - timedelta(days=random.randint(1, 180)),
            'subscription_end_date': timezone.now().date() + timedelta(days=30),
            'payment_method': random.choice(['Bank Transfer', 'PayPal', 'Credit Card']),
            'payment_reference': f'PAY{random.randint(100000, 999999)}',
            'notes': 'Sample subscription data'
        }
    )
    if created:
        print(f'Created subscription for {hostel.name}')

print(f'Update complete! Updated {updated_count} hostels.')
