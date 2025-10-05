#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_platform.settings')
django.setup()

from hostels.models import User, Hostel, Review
from django.contrib.auth.hashers import make_password

def create_test_reviews():
    # Get or create test users
    student1, created = User.objects.get_or_create(
        email='student1@test.com',
        defaults={
            'username': 'student1',
            'password': make_password('testpass123'),
            'role': 'student',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    )
    if created:
        print(f"Created user: {student1.username}")

    student2, created = User.objects.get_or_create(
        email='student2@test.com',
        defaults={
            'username': 'student2',
            'password': make_password('testpass123'),
            'role': 'student',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
    )
    if created:
        print(f"Created user: {student2.username}")

    # Get first hostel
    hostel = Hostel.objects.filter(is_active=True).first()

    if hostel:
        print(f"Found hostel: {hostel.name}")

        # Create sample reviews
        review1, created = Review.objects.get_or_create(
            user=student1,
            hostel=hostel,
            defaults={
                'rating': 5,
                'review_text': 'Excellent hostel! Clean rooms, great facilities, and very helpful staff. Highly recommended for students.',
                'is_approved': True
            }
        )
        if created:
            print(f"Created 5-star review by {student1.first_name}")

        review2, created = Review.objects.get_or_create(
            user=student2,
            hostel=hostel,
            defaults={
                'rating': 4,
                'review_text': 'Good hostel with decent amenities. The location is perfect and the price is reasonable. Would stay here again.',
                'is_approved': True
            }
        )
        if created:
            print(f"Created 4-star review by {student2.first_name}")

        # Test rating properties
        print(f"\n=== Hostel Rating Summary ===")
        print(f"Hostel: {hostel.name}")
        print(f"Average Rating: {hostel.average_rating}")
        print(f"Total Reviews: {hostel.rating_count}")
        print(f"Star Display: {hostel.rating_stars_display}")
        print(f"Rating Distribution: {hostel.rating_distribution}")

    else:
        print("No active hostel found")

if __name__ == '__main__':
    create_test_reviews()
