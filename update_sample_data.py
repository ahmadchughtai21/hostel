#!/usr/bin/env python3
"""
Script to update existing hostels with new landmark and featured data
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_platform.settings')
django.setup()

from hostels.models import Hostel, HostelSubscription
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

def update_hostels():
    """Update existing hostels with landmark information and featured status"""

    # Sample landmarks (universities, colleges, workplaces)
    landmarks = [
        ("Harvard University", 0.8),
        ("MIT", 1.2),
        ("Stanford University", 0.5),
        ("UC Berkeley", 1.5),
        ("Tech Hub Downtown", 2.0),
        ("Business District Center", 1.8),
        ("Community College", 0.3),
        ("Medical Center", 1.0),
        ("Research Park", 2.5),
        ("City University", 0.7),
        ("Engineering Campus", 1.3),
        ("Innovation Center", 1.9),
    ]

    # Sample Google Maps links
    google_maps_links = [
        "https://maps.google.com/maps?q=37.7749,-122.4194",
        "https://maps.google.com/maps?q=40.7128,-74.0060",
        "https://maps.google.com/maps?q=34.0522,-118.2437",
        "https://maps.google.com/maps?q=41.8781,-87.6298",
        "https://maps.google.com/maps?q=29.7604,-95.3698",
    ]

    hostels = Hostel.objects.all()

    for i, hostel in enumerate(hostels):
        # Add landmark information to about 80% of hostels
        if random.random() < 0.8:
            landmark, distance = random.choice(landmarks)
            hostel.nearby_landmark = landmark
            hostel.landmark_distance = Decimal(str(distance))

        # Add Google Maps link to about 60% of hostels
        if random.random() < 0.6:
            hostel.google_location_link = random.choice(google_maps_links)

        # Make about 20% of hostels featured
        if random.random() < 0.2:
            hostel.is_featured = True

        hostel.save()
        print(f"Updated {hostel.name}")

        # Create subscription for each hostel
        subscription, created = HostelSubscription.objects.get_or_create(
            hostel=hostel,
            defaults={
                'monthly_fee': Decimal('29.99'),
                'status': 'active' if hostel.is_verified else 'pending',
                'subscription_start_date': timezone.now().date() - timedelta(days=random.randint(1, 365)),
                'subscription_end_date': timezone.now().date() + timedelta(days=30),
                'payment_method': random.choice(['Bank Transfer', 'PayPal', 'Credit Card']),
                'payment_reference': f"PAY{random.randint(100000, 999999)}",
                'notes': 'Auto-generated subscription record'
            }
        )

        if created:
            print(f"Created subscription for {hostel.name}")

if __name__ == '__main__':
    print("Updating hostels with new landmark and featured data...")
    update_hostels()
    print("Update complete!")
