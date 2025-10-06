"""
Management command to create initial featured advertising plans
"""
from django.core.management.base import BaseCommand
from hostels.models import FeaturedPlan


class Command(BaseCommand):
    help = 'Create initial featured advertising plans'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': '1-Day Boost',
                'duration_type': '1_day',
                'duration_days': 1,
                'price': 500.00,
                'description': 'Quick visibility boost for your hostel. Perfect for special announcements or immediate exposure.',
                'is_active': True
            },
            {
                'name': '1-Week Premium',
                'duration_type': '1_week',
                'duration_days': 7,
                'price': 2500.00,
                'description': 'One week of premium visibility. Great for attracting students during peak booking seasons.',
                'is_active': True
            },
            {
                'name': '1-Month Platinum',
                'duration_type': '1_month',
                'duration_days': 30,
                'price': 8000.00,
                'description': 'Maximum exposure for a full month. Best value for consistent high visibility and bookings.',
                'is_active': True
            }
        ]

        created_count = 0
        for plan_data in plans_data:
            plan, created = FeaturedPlan.objects.get_or_create(
                duration_type=plan_data['duration_type'],
                defaults=plan_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new plans')
        )
