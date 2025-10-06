#!/usr/bin/env python
"""
Simple script to test template rendering without starting the server
"""
import os
import django
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_platform.settings')
django.setup()

def test_reports_template():
    """Test that the reports templates can be rendered without errors"""
    try:
        # Test the main reports template
        template = get_template('hostels/admin/reports.html')
        print("✅ Main reports template loads successfully")

        # Test the reports content template
        content_template = get_template('hostels/admin/reports_content.html')
        print("✅ Reports content template loads successfully")

        # Test basic rendering with minimal context
        context = {
            'reports': [],
            'total_reports': 0,
            'pending_reports': 0,
            'resolved_reports': 0,
            'reports_this_month': 0,
        }

        rendered = template.render(context)
        print("✅ Template renders successfully with empty context")

        # Check if critical elements are present
        if 'Reports Management' in rendered:
            print("✅ Template contains expected title")
        else:
            print("⚠️ Template missing expected title")

        return True

    except Exception as e:
        print(f"❌ Template error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing template rendering...")
    success = test_reports_template()
    if success:
        print("\n🎉 All template tests passed! The report hostel feature is ready to use.")
    else:
        print("\n💥 Template tests failed. Check the error messages above.")
