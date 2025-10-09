#!/usr/bin/env python
"""
Quick test script to verify view tracking functionality
"""

import os
import django
import requests
from time import sleep

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_platform.settings')
django.setup()

from hostels.models import Hostel, HostelView

def test_view_tracking():
    print("Testing View Tracking System...")
    print("=" * 50)

    # Get first hostel
    hostel = Hostel.objects.first()
    if not hostel:
        print("No hostels found. Please create some sample data first.")
        return

    print(f"Testing with hostel: {hostel.name}")
    print(f"Hostel slug: {hostel.slug}")

    # Check current view count
    initial_views = hostel.views_count
    print(f"Initial views count: {initial_views}")

    # Make a request to the hostel detail page
    url = f"http://127.0.0.1:8000/hostels/{hostel.slug}/"
    print(f"Making request to: {url}")

    try:
        response = requests.get(url)
        print(f"Response status: {response.status_code}")

        # Wait a moment for the view to be recorded
        sleep(1)

        # Check new view count
        hostel.refresh_from_db()
        new_views = hostel.views_count
        print(f"New views count: {new_views}")

        if new_views > initial_views:
            print("✅ View tracking is working correctly!")

            # Get the latest view record
            latest_view = HostelView.objects.filter(hostel=hostel).latest('timestamp')
            print(f"Latest view details:")
            print(f"  - IP: {latest_view.ip_address}")
            print(f"  - Timestamp: {latest_view.timestamp}")
            print(f"  - User: {latest_view.user or 'Anonymous'}")

        else:
            print("❌ View tracking is not working. Views count didn't increase.")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Django server. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_view_tracking()
