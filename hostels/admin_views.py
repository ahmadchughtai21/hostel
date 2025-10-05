from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Hostel, User, ContactReveal
import json

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.role == 'admin' or self.request.user.is_superuser
        )


class ApproveHostelView(AdminRequiredMixin, View):
    """AJAX view to approve a hostel"""

    def post(self, request, hostel_id):
        try:
            hostel = get_object_or_404(Hostel, id=hostel_id)
            hostel.is_verified = True
            hostel.save()

            return JsonResponse({
                'success': True,
                'message': f'Hostel "{hostel.name}" has been approved successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class RejectHostelView(AdminRequiredMixin, View):
    """AJAX view to reject a hostel"""

    def post(self, request, hostel_id):
        try:
            data = json.loads(request.body) if request.body else {}
            reason = data.get('reason', '')

            hostel = get_object_or_404(Hostel, id=hostel_id)
            hostel.is_active = False
            hostel.save()

            # Here you could send an email to the owner with the rejection reason
            # send_rejection_email(hostel.owner, hostel, reason)

            return JsonResponse({
                'success': True,
                'message': f'Hostel "{hostel.name}" has been rejected.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class ToggleFeaturedView(AdminRequiredMixin, View):
    """AJAX view to toggle featured status of a hostel"""

    def post(self, request, hostel_id):
        try:
            hostel = get_object_or_404(Hostel, id=hostel_id)
            hostel.is_featured = not hostel.is_featured
            hostel.save()

            return JsonResponse({
                'success': True,
                'is_featured': hostel.is_featured,
                'message': f'Hostel "{hostel.name}" {"added to" if hostel.is_featured else "removed from"} featured list.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class ToggleActiveView(AdminRequiredMixin, View):
    """AJAX view to toggle active status of a hostel"""

    def post(self, request, hostel_id):
        try:
            hostel = get_object_or_404(Hostel, id=hostel_id)
            hostel.is_active = not hostel.is_active
            hostel.save()

            return JsonResponse({
                'success': True,
                'is_active': hostel.is_active,
                'message': f'Hostel "{hostel.name}" has been {"activated" if hostel.is_active else "deactivated"}.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class BulkHostelActionView(AdminRequiredMixin, View):
    """AJAX view for bulk operations on hostels"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            hostel_ids = data.get('hostel_ids', [])

            if not action or not hostel_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Action and hostel IDs are required'
                }, status=400)

            hostels = Hostel.objects.filter(id__in=hostel_ids)

            if action == 'approve':
                hostels.update(is_verified=True)
                message = f'{hostels.count()} hostels approved successfully.'
            elif action == 'reject':
                hostels.update(is_active=False, is_verified=False)
                message = f'{hostels.count()} hostels rejected successfully.'
            elif action == 'feature':
                hostels.update(is_featured=True)
                message = f'{hostels.count()} hostels added to featured list.'
            elif action == 'unfeature':
                hostels.update(is_featured=False)
                message = f'{hostels.count()} hostels removed from featured list.'
            elif action == 'activate':
                hostels.update(is_active=True)
                message = f'{hostels.count()} hostels activated successfully.'
            elif action == 'deactivate':
                hostels.update(is_active=False)
                message = f'{hostels.count()} hostels deactivated successfully.'
            elif action == 'delete':
                count = hostels.count()
                hostels.delete()
                message = f'{count} hostels deleted successfully.'
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'affected_count': count
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action'
                }, status=400)

            return JsonResponse({
                'success': True,
                'message': message,
                'affected_count': hostels.count()
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class ExportDataView(AdminRequiredMixin, View):
    """Export data to CSV"""

    def get(self, request):
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        export_type = request.GET.get('type', 'hostels')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{export_type}_{datetime.now().strftime("%Y%m%d")}.csv"'

        writer = csv.writer(response)

        if export_type == 'hostels':
            writer.writerow(['ID', 'Name', 'Owner', 'Address', 'Min Price', 'Verified', 'Featured', 'Active', 'Created'])

            hostels = Hostel.objects.select_related('owner').all()
            for hostel in hostels:
                writer.writerow([
                    str(hostel.id),
                    hostel.name,
                    hostel.owner.get_full_name() or hostel.owner.username,
                    hostel.address,
                    hostel.min_price or 'N/A',
                    'Yes' if hostel.is_verified else 'No',
                    'Yes' if hostel.is_featured else 'No',
                    'Yes' if hostel.is_active else 'No',
                    hostel.created_at.strftime('%Y-%m-%d %H:%M')
                ])

        elif export_type == 'users':
            writer.writerow(['ID', 'Username', 'Full Name', 'Email', 'Role', 'Verified', 'Joined'])

            users = User.objects.all()
            for user in users:
                writer.writerow([
                    str(user.id),
                    user.username,
                    user.get_full_name(),
                    user.email,
                    user.get_role_display(),
                    'Yes' if user.email_verified else 'No',
                    user.date_joined.strftime('%Y-%m-%d %H:%M')
                ])

        return response


class SystemBackupView(AdminRequiredMixin, View):
    """Create a backup of essential data"""

    def get(self, request):
        import json
        from django.http import HttpResponse
        from datetime import datetime
        from django.core import serializers

        # Create backup data
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'data': {
                'hostels': json.loads(serializers.serialize('json', Hostel.objects.all())),
                'users': json.loads(serializers.serialize('json', User.objects.all())),
                'contact_reveals': json.loads(serializers.serialize('json', ContactReveal.objects.all())),
            }
        }

        response = HttpResponse(
            json.dumps(backup_data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="hostel_platform_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'

        return response


class DeleteHostelView(AdminRequiredMixin, View):
    """AJAX view to delete a hostel"""

    def post(self, request, hostel_id):
        try:
            hostel = get_object_or_404(Hostel, id=hostel_id)
            hostel_name = hostel.name
            hostel.delete()

            return JsonResponse({
                'success': True,
                'message': f'Hostel "{hostel_name}" has been deleted successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class DeleteUserView(AdminRequiredMixin, View):
    """AJAX view to delete a user"""

    def post(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)

            # Prevent deletion of superusers and the current admin
            if user.is_superuser:
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot delete superuser accounts.'
                }, status=400)

            if user == request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot delete your own account.'
                }, status=400)

            username = user.username
            user.delete()

            return JsonResponse({
                'success': True,
                'message': f'User "{username}" has been deleted successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class BulkUserActionView(AdminRequiredMixin, View):
    """AJAX view for bulk operations on users"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            user_ids = data.get('user_ids', [])

            if not action or not user_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Action and user IDs are required'
                }, status=400)

            users = User.objects.filter(id__in=user_ids)

            # Filter out superusers and current user for safety
            if action in ['delete', 'deactivate']:
                users = users.exclude(is_superuser=True).exclude(id=request.user.id)

            if action == 'activate':
                users.update(is_active=True)
                message = f'{users.count()} users activated successfully.'
            elif action == 'deactivate':
                users.update(is_active=False)
                message = f'{users.count()} users deactivated successfully.'
            elif action == 'delete':
                count = users.count()
                users.delete()
                message = f'{count} users deleted successfully.'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action'
                }, status=400)

            return JsonResponse({
                'success': True,
                'message': message,
                'affected_count': users.count() if action != 'delete' else count
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class ApproveReviewView(AdminRequiredMixin, View):
    """Approve a review"""

    def post(self, request, review_id):
        try:
            from .models import Review
            review = get_object_or_404(Review, id=review_id)
            review.is_approved = True
            review.save()

            return JsonResponse({
                'success': True,
                'message': 'Review approved successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class UnapproveReviewView(AdminRequiredMixin, View):
    """Unapprove a review"""

    def post(self, request, review_id):
        try:
            from .models import Review
            review = get_object_or_404(Review, id=review_id)
            review.is_approved = False
            review.save()

            return JsonResponse({
                'success': True,
                'message': 'Review unapproved successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class DeleteReviewAdminView(AdminRequiredMixin, View):
    """Delete a review (admin only)"""

    def post(self, request, review_id):
        try:
            from .models import Review
            review = get_object_or_404(Review, id=review_id)
            review.delete()

            return JsonResponse({
                'success': True,
                'message': 'Review deleted successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
