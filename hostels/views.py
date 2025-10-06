from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.urls import reverse_lazy
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from decimal import Decimal
import requests
import json

from .models import Hostel, User, Review, Category, RoomType, Facility, ContactReveal, Favorite, Item, HostelImage, Report, FeaturedPlan, FeaturedRequest, FeaturedHistory
from .forms import UserRegistrationForm, UserProfileForm, HostelForm, ReportForm, FeaturedRequestForm, FeaturedPlanForm, FeaturedRequestReviewForm

# Dashboard views
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'hostels/dashboard/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'user': user,
        })
        return context

class OwnerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'hostels/owner/dashboard.html'

    def test_func(self):
        return self.request.user.role == 'owner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get hostels with prefetch for optimization
        hostels = user.hostels.all().select_related().prefetch_related(
            'featured_requests', 'contact_reveals'
        ).order_by('-created_at')

        # Calculate featured hostels count
        featured_count = sum(1 for hostel in hostels if hostel.is_currently_featured)

        # Get pending featured requests
        pending_requests = FeaturedRequest.objects.filter(
            owner=user,
            status='pending'
        ).select_related('hostel', 'plan')

        # Calculate total contact reveals across all hostels
        total_reveals = sum(hostel.contact_reveals_count for hostel in hostels)

        context.update({
            'hostels': hostels,
            'total_hostels': hostels.count(),
            'verified_hostels': hostels.filter(is_verified=True).count(),
            'pending_hostels': hostels.filter(is_verified=False).count(),
            'featured_hostels': featured_count,
            'total_contact_reveals': total_reveals,
            'pending_featured_requests': pending_requests,
        })
        return context

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'hostels/dashboard/admin.html'

    def test_func(self):
        return self.request.user.role == 'admin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()

        context.update({
            'total_users': User.objects.count(),
            'total_hostels': Hostel.objects.count(),
            'pending_hostels': Hostel.objects.filter(is_verified=False).count(),
            'recent_users': User.objects.order_by('-date_joined')[:10],
            'recent_hostels': Hostel.objects.order_by('-created_at')[:10],
        })
        return context


class HomeView(TemplateView):
    """Home page with search and featured hostels"""
    template_name = 'hostels/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Featured hostels section - show actual featured hostels
        context['featured_hostels'] = Hostel.objects.filter(
            is_featured=True, is_verified=True, is_active=True
        ).order_by('-created_at')[:6]

        # If we don't have enough featured hostels, fill with recent ones
        if context['featured_hostels'].count() < 6:
            featured_count = context['featured_hostels'].count()
            additional_hostels = Hostel.objects.filter(
                is_verified=True, is_active=True
            ).exclude(
                id__in=context['featured_hostels'].values_list('id', flat=True)
            ).order_by('-created_at')[:6-featured_count]

            context['featured_hostels'] = list(context['featured_hostels']) + list(additional_hostels)

        context['facilities'] = Facility.objects.all()
        return context


class HostelListView(ListView):
    """List/grid view of hostels with filters"""
    model = Hostel
    template_name = 'hostels/hostel_list.html'
    context_object_name = 'hostels'
    paginate_by = 12

    def get_queryset(self):
        queryset = Hostel.objects.filter(is_verified=True, is_active=True)

        # Search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(address__icontains=query) | Q(nearby_landmark__icontains=query)
            )

        # Landmark proximity filter
        landmark = self.request.GET.get('landmark')
        if landmark:
            queryset = queryset.filter(nearby_landmark__icontains=landmark)

        # Distance filter
        max_distance = self.request.GET.get('max_distance')
        if max_distance:
            try:
                max_distance = Decimal(max_distance)
                queryset = queryset.filter(landmark_distance__lte=max_distance)
            except (ValueError, TypeError):
                pass

        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(room_types__price__gte=min_price)
        if max_price:
            queryset = queryset.filter(room_types__price__lte=max_price)

        # Facilities filter
        facilities = self.request.GET.getlist('facilities')
        if facilities:
            queryset = queryset.filter(hostel_facilities__facility__id__in=facilities)

        # Room type filter
        room_type = self.request.GET.get('room_type')
        if room_type:
            queryset = queryset.filter(room_types__type=room_type)

        # Gender type filter
        gender_type = self.request.GET.get('gender_type')
        if gender_type:
            queryset = queryset.filter(gender_type=gender_type)

        # Rating filter
        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            try:
                min_rating = int(min_rating)
                queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=min_rating)
            except (ValueError, TypeError):
                pass

        # Sorting
        sort_by = self.request.GET.get('sort', 'featured')
        if sort_by == 'featured':
            queryset = queryset.order_by('-is_featured', '-created_at')
        elif sort_by == 'price_low':
            queryset = queryset.order_by('room_types__price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-room_types__price')
        elif sort_by == 'distance':
            queryset = queryset.filter(landmark_distance__isnull=False).order_by('landmark_distance')
        elif sort_by == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        else:  # newest
            queryset = queryset.order_by('-created_at')

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facilities'] = Facility.objects.all()
        context['room_types'] = RoomType.ROOM_TYPE_CHOICES

        # Add rating filter options
        context['rating_options'] = [
            {'value': '4', 'label': '4+ Stars'},
            {'value': '3', 'label': '3+ Stars'},
            {'value': '2', 'label': '2+ Stars'},
            {'value': '1', 'label': '1+ Star'},
        ]

        return context


class HostelDetailView(DetailView):
    """Detailed view of a single hostel"""
    model = Hostel
    template_name = 'hostels/hostel_detail.html'
    context_object_name = 'hostel'

    def get_queryset(self):
        return Hostel.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        from django.db.models import Min, Max
        context = super().get_context_data(**kwargs)
        room_types = self.object.room_types.all().order_by('price')
        context['room_types'] = room_types
        context['facilities'] = self.object.hostel_facilities.all()
        context['images'] = self.object.images.all()

        # Review and rating data
        approved_reviews = self.object.reviews.filter(is_approved=True).order_by('-created_at')
        context['reviews'] = approved_reviews
        context['reviews_count'] = approved_reviews.count()
        context['average_rating'] = self.object.average_rating
        context['rating_distribution'] = self.object.rating_distribution
        context['rating_stars'] = self.object.rating_stars_display

        # Check if current user has reviewed this hostel
        context['user_review'] = None
        context['can_review'] = False
        if self.request.user.is_authenticated:
            user_review = self.object.reviews.filter(user=self.request.user).first()
            context['user_review'] = user_review
            context['can_review'] = user_review is None  # Can only review if haven't already

        context['is_favorite'] = False

        # Calculate price range safely
        if room_types.exists():
            price_range = room_types.aggregate(
                min_price=Min('price'),
                max_price=Max('price')
            )
            context['min_price'] = price_range['min_price']
            context['max_price'] = price_range['max_price']
        else:
            context['min_price'] = None
            context['max_price'] = None

        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user, hostel=self.object
            ).exists()

        return context


class RevealContactView(View):
    """AJAX view to reveal contact information and track it"""

    def post(self, request, slug):
        # Check for AJAX request (modern browsers may not have is_ajax method)
        if not (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                request.content_type == 'application/json'):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        hostel = get_object_or_404(Hostel, slug=slug, is_active=True)

        # Track the contact reveal
        ContactReveal.objects.create(
            hostel=hostel,
            user=request.user if request.user.is_authenticated else None,
            ip_address=self.get_client_ip(request)
        )

        return JsonResponse({
            'contact_email': hostel.contact_email,
            'contact_phone': hostel.contact_phone,
            'whatsapp_number': hostel.whatsapp_number,
        })

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Authentication Views
class LoginView(AuthLoginView):
    template_name = 'hostels/auth/login.html'
    redirect_authenticated_user = True


class LogoutView(AuthLogoutView):
    next_page = 'hostels:home'


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'hostels/auth/register.html'
    success_url = reverse_lazy('hostels:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Account created successfully!')
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'hostels/auth/profile.html'
    success_url = reverse_lazy('hostels:profile')

    def get_object(self):
        return self.request.user


# Owner Dashboard Views
class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'owner'


class OwnerDashboardView(OwnerRequiredMixin, TemplateView):
    template_name = 'hostels/owner/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_hostels = self.request.user.hostels.all()

        context['hostels'] = user_hostels
        context['total_hostels'] = user_hostels.count()
        context['verified_hostels'] = user_hostels.filter(is_verified=True).count()
        context['total_contact_reveals'] = sum(h.contact_reveals_count for h in user_hostels)

        return context


class AddHostelView(OwnerRequiredMixin, CreateView):
    model = Hostel
    form_class = HostelForm
    template_name = 'hostels/owner/add_hostel.html'

    def get_success_url(self):
        return reverse_lazy('hostels:edit_hostel', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        from .forms import HostelImageFormSet, RoomTypeFormSet
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['image_formset'] = HostelImageFormSet(self.request.POST, self.request.FILES)
            context['room_formset'] = RoomTypeFormSet(self.request.POST)
        else:
            context['image_formset'] = HostelImageFormSet(queryset=HostelImage.objects.none())
            context['room_formset'] = RoomTypeFormSet(queryset=RoomType.objects.none())

        # Add facilities for the template
        context['facilities'] = Facility.objects.all()
        return context

    def form_valid(self, form):
        try:
            from .forms import HostelImageFormSet, RoomTypeFormSet
            context = self.get_context_data()
            image_formset = context['image_formset']
            room_formset = context['room_formset']

            # Validate the main form first
            if not form.is_valid():
                messages.error(self.request, 'Please correct the errors in the hostel form.')
                return self.form_invalid(form)

            # Set owner and save the hostel
            form.instance.owner = self.request.user
            self.object = form.save()

            # Handle formsets with error catching
            images_saved = 0
            rooms_saved = 0

            # Try to save images if formset is valid
            try:
                if image_formset.is_valid():
                    images = image_formset.save(commit=False)
                    for image in images:
                        if hasattr(image, 'image') and image.image:
                            image.hostel = self.object
                            image.save()
                            images_saved += 1
                elif image_formset.errors:
                    print("Image formset errors:", image_formset.errors)
            except Exception as e:
                print(f"Error saving images: {e}")

            # Try to save room types if formset is valid
            try:
                if room_formset.is_valid():
                    rooms = room_formset.save(commit=False)
                    for room in rooms:
                        if hasattr(room, 'type') and room.type and hasattr(room, 'price') and room.price:
                            room.hostel = self.object
                            room.save()
                            rooms_saved += 1
                elif room_formset.errors:
                    print("Room formset errors:", room_formset.errors)
            except Exception as e:
                print(f"Error saving rooms: {e}")

            success_msg = f'Hostel "{self.object.name}" added successfully!'
            if images_saved:
                success_msg += f' Added {images_saved} images.'
            if rooms_saved:
                success_msg += f' Added {rooms_saved} room types.'

            messages.success(self.request, success_msg)
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(self.request, f'An error occurred while saving: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class EditHostelView(OwnerRequiredMixin, UpdateView):
    model = Hostel
    form_class = HostelForm
    template_name = 'hostels/owner/edit_hostel.html'

    def get_queryset(self):
        return self.request.user.hostels.all()

    def get_success_url(self):
        return reverse_lazy('hostels:hostel_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        from .forms import HostelImageFormSet, RoomTypeFormSet
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['image_formset'] = HostelImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
            context['room_formset'] = RoomTypeFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['image_formset'] = HostelImageFormSet(instance=self.object)
            context['room_formset'] = RoomTypeFormSet(instance=self.object)

        # Add facilities for the template
        context['facilities'] = Facility.objects.all()
        return context

    def form_valid(self, form):
        try:
            from .forms import HostelImageFormSet, RoomTypeFormSet
            context = self.get_context_data()
            image_formset = context['image_formset']
            room_formset = context['room_formset']

            # Validate the main form first
            if not form.is_valid():
                messages.error(self.request, 'Please correct the errors in the hostel form.')
                return self.form_invalid(form)

            # Save the hostel
            self.object = form.save()

            # Handle formsets with error catching
            images_saved = 0
            rooms_saved = 0
            rooms_deleted = 0

            # Try to save images if formset is valid
            try:
                if image_formset.is_valid():
                    images = image_formset.save(commit=False)
                    for image in images:
                        if hasattr(image, 'image') and image.image:
                            image.hostel = self.object
                            image.save()
                            images_saved += 1
                    # Handle deleted images
                    for obj in image_formset.deleted_objects:
                        obj.delete()
                elif image_formset.errors:
                    print("Image formset errors:", image_formset.errors)
            except Exception as e:
                print(f"Error saving images: {e}")

            # Try to save room types if formset is valid
            try:
                if room_formset.is_valid():
                    rooms = room_formset.save(commit=False)
                    for room in rooms:
                        if hasattr(room, 'type') and room.type and hasattr(room, 'price') and room.price:
                            room.hostel = self.object
                            room.save()
                            rooms_saved += 1
                    # Handle deleted room types
                    for obj in room_formset.deleted_objects:
                        obj.delete()
                        rooms_deleted += 1
                elif room_formset.errors:
                    print("Room formset errors:", room_formset.errors)
            except Exception as e:
                print(f"Error saving rooms: {e}")

            success_msg = f'Hostel "{self.object.name}" updated successfully!'
            if images_saved:
                success_msg += f' Updated {images_saved} images.'
            if rooms_saved:
                success_msg += f' Updated {rooms_saved} room types.'
            if rooms_deleted:
                success_msg += f' Removed {rooms_deleted} room types.'

            messages.success(self.request, success_msg)
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(self.request, f'An error occurred while saving: {str(e)}')
            return self.form_invalid(form)


class DeleteHostelView(OwnerRequiredMixin, DeleteView):
    model = Hostel
    template_name = 'hostels/owner/delete_hostel.html'
    success_url = reverse_lazy('hostels:owner_dashboard')

    def get_queryset(self):
        return self.request.user.hostels.all()


# Student Features
class FavoritesView(LoginRequiredMixin, ListView):
    template_name = 'hostels/student/favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return self.request.user.favorites.all()


class AddToFavoritesView(LoginRequiredMixin, View):
    def post(self, request, slug):
        hostel = get_object_or_404(Hostel, slug=slug)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, hostel=hostel
        )

        if created:
            messages.success(request, f'{hostel.name} added to favorites!')
        else:
            messages.info(request, f'{hostel.name} is already in your favorites.')

        return redirect('hostels:hostel_detail', slug=slug)


class RemoveFromFavoritesView(LoginRequiredMixin, View):
    def post(self, request, slug):
        hostel = get_object_or_404(Hostel, slug=slug)
        Favorite.objects.filter(user=request.user, hostel=hostel).delete()
        messages.success(request, f'{hostel.name} removed from favorites!')
        return redirect('hostels:favorites')


# Admin Views
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.role == 'admin' or self.request.user.is_superuser
        )


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'hostels/admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_hostels'] = Hostel.objects.count()
        context['verified_hostels'] = Hostel.objects.filter(is_verified=True).count()
        context['pending_hostels'] = Hostel.objects.filter(is_verified=False).count()
        context['featured_hostels'] = Hostel.objects.filter(is_featured=True).count()
        context['total_users'] = User.objects.count()
        context['total_owners'] = User.objects.filter(role='owner').count()
        context['total_students'] = User.objects.filter(role='student').count()
        context['total_contact_reveals'] = ContactReveal.objects.count()
        context['pending_reviews_count'] = Review.objects.filter(is_approved=False).count()
        context['pending_featured_requests'] = FeaturedRequest.objects.filter(status='pending').count()

        # Recent data for dashboard with contact reveal counts
        recent_hostels = Hostel.objects.select_related('owner').prefetch_related('images', 'contact_reveals').order_by('-created_at')[:10]
        context['recent_hostels'] = recent_hostels
        context['recent_users'] = User.objects.order_by('-date_joined')[:10]

        # Analytics data
        from django.utils import timezone
        from datetime import timedelta

        thirty_days_ago = timezone.now() - timedelta(days=30)
        context['new_hostels_this_month'] = Hostel.objects.filter(created_at__gte=thirty_days_ago).count()
        context['new_users_this_month'] = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        context['contact_reveals_this_month'] = ContactReveal.objects.filter(timestamp__gte=thirty_days_ago).count()

        return context


class PendingHostelsView(AdminRequiredMixin, ListView):
    model = Hostel
    template_name = 'hostels/admin/pending_hostels.html'
    context_object_name = 'hostels'

    def get_queryset(self):
        return Hostel.objects.filter(is_verified=False, is_active=True)


class AdminHostelListView(AdminRequiredMixin, ListView):
    model = Hostel
    template_name = 'hostels/admin/hostel_management.html'
    context_object_name = 'hostels'
    paginate_by = 20

    def get_queryset(self):
        queryset = Hostel.objects.select_related('owner').prefetch_related('images')

        # Apply filters
        status = self.request.GET.get('status')
        if status == 'verified':
            queryset = queryset.filter(is_verified=True)
        elif status == 'pending':
            queryset = queryset.filter(is_verified=False)
        elif status == 'featured':
            queryset = queryset.filter(is_featured=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(owner__username__icontains=search) |
                Q(address__icontains=search)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', 'all')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class AdminUserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'hostels/admin/user_management.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all()

        # Apply filters
        role = self.request.GET.get('role')
        if role in ['student', 'owner', 'admin']:
            queryset = queryset.filter(role=role)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset.order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_role'] = self.request.GET.get('role', 'all')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class AdminAnalyticsView(AdminRequiredMixin, TemplateView):
    template_name = 'hostels/admin/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count

        # Date ranges
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        last_year = now - timedelta(days=365)

        # Hostel statistics
        verified_count = Hostel.objects.filter(is_verified=True).count()
        context['hostel_stats'] = {
            'total': Hostel.objects.count(),
            'verified': verified_count,
            'pending': Hostel.objects.filter(is_verified=False).count(),
            'featured': Hostel.objects.filter(is_featured=True).count(),
            'new_this_month': Hostel.objects.filter(created_at__gte=last_30_days).count(),
            'estimated_revenue': verified_count * 8999,  # Calculate revenue in view
        }

        # User statistics
        context['user_stats'] = {
            'total': User.objects.count(),
            'students': User.objects.filter(role='student').count(),
            'owners': User.objects.filter(role='owner').count(),
            'admins': User.objects.filter(role='admin').count(),
            'new_this_month': User.objects.filter(date_joined__gte=last_30_days).count(),
        }

        # Contact reveal statistics
        context['contact_stats'] = {
            'total': ContactReveal.objects.count(),
            'this_week': ContactReveal.objects.filter(timestamp__gte=last_7_days).count(),
            'this_month': ContactReveal.objects.filter(timestamp__gte=last_30_days).count(),
        }

        # Monthly registration trends
        monthly_registrations = User.objects.filter(
            date_joined__gte=last_year
        ).extra(
            select={'month': 'strftime("%%Y-%%m", date_joined)'}
        ).values('month').annotate(count=Count('id')).order_by('month')

        # Add calculated heights for chart display
        monthly_data = []
        for item in monthly_registrations:
            monthly_data.append({
                'month': item['month'],
                'count': item['count'],
                'height': item['count'] * 20  # Calculate height in view
            })

        context['monthly_registrations'] = monthly_data

        return context


class ReportsView(AdminRequiredMixin, ListView):
    """Admin view to manage hostel reports"""
    model = Report
    template_name = 'hostels/admin/reports.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        return Report.objects.select_related('hostel', 'reporter', 'resolved_by').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'pending_reports': Report.objects.filter(is_resolved=False).count(),
            'total_reports': Report.objects.count(),
            'resolved_reports': Report.objects.filter(is_resolved=True).count(),
        })
        return context


class ReportHostelView(LoginRequiredMixin, CreateView):
    """View for reporting a hostel"""
    model = Report
    form_class = ReportForm
    template_name = 'hostels/report_hostel.html'

    def get_hostel(self):
        return get_object_or_404(Hostel, slug=self.kwargs['slug'])

    def form_valid(self, form):
        form.instance.hostel = self.get_hostel()
        form.instance.reporter = self.request.user
        messages.success(self.request, 'Report submitted successfully. We will review it shortly.')
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_hostel().get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hostel'] = self.get_hostel()
        return context


class ResolveReportView(AdminRequiredMixin, View):
    """AJAX view for resolving reports"""

    def post(self, request, report_id):
        try:
            report = get_object_or_404(Report, id=report_id)
            report.is_resolved = True
            report.resolved_by = request.user
            report.resolved_at = timezone.now()
            report.save()

            return JsonResponse({
                'success': True,
                'message': 'Report resolved successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })


class DeleteReportView(AdminRequiredMixin, View):
    """AJAX view for permanently deleting reports"""

    def post(self, request, report_id):
        try:
            report = get_object_or_404(Report, id=report_id)
            hostel_name = report.hostel.name
            report.delete()

            return JsonResponse({
                'success': True,
                'message': f'Report for {hostel_name} has been permanently deleted'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })


# API Views
class GeocodeView(View):
    """Geocode address using Google Maps API"""

    def post(self, request):
        if not request.is_ajax():
            return JsonResponse({'error': 'Invalid request'}, status=400)

        address = request.POST.get('address')
        if not address:
            return JsonResponse({'error': 'Address is required'}, status=400)

        # Mock geocoding - replace with actual Google Maps API call
        # This is a placeholder for the actual implementation
        return JsonResponse({
            'latitude': 31.5204,  # Lahore coordinates as example
            'longitude': 74.3587,
            'formatted_address': address
        })


class SearchAPIView(View):
    """API endpoint for autocomplete search"""

    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'results': []})

        hostels = Hostel.objects.filter(
            Q(name__icontains=query) | Q(address__icontains=query),
            is_verified=True, is_active=True
        )[:10]

        results = [
            {
                'id': hostel.id,
                'name': hostel.name,
                'address': hostel.address,
                'url': hostel.get_absolute_url()
            }
            for hostel in hostels
        ]

        return JsonResponse({'results': results})


# Review and Rating Views
class AddReviewView(LoginRequiredMixin, View):
    """Add a review for a hostel"""

    def post(self, request, slug):
        hostel = get_object_or_404(Hostel, slug=slug, is_verified=True, is_active=True)

        # Check if user has already reviewed this hostel
        existing_review = Review.objects.filter(hostel=hostel, user=request.user).first()
        if existing_review:
            return JsonResponse({
                'success': False,
                'error': 'You have already reviewed this hostel.'
            }, status=400)

        try:
            rating = int(request.POST.get('rating'))
            review_text = request.POST.get('review_text', '').strip()

            if not (1 <= rating <= 5):
                return JsonResponse({
                    'success': False,
                    'error': 'Rating must be between 1 and 5 stars.'
                }, status=400)

            if len(review_text) < 10:
                return JsonResponse({
                    'success': False,
                    'error': 'Review must be at least 10 characters long.'
                }, status=400)

            # Create the review
            review = Review.objects.create(
                hostel=hostel,
                user=request.user,
                rating=rating,
                review_text=review_text,
                is_approved=False  # Reviews need admin approval
            )

            return JsonResponse({
                'success': True,
                'message': 'Your review has been submitted and is pending approval.'
            })

        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid rating value.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while submitting your review.'
            }, status=500)


class UpdateReviewView(LoginRequiredMixin, View):
    """Update an existing review"""

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)

        try:
            rating = int(request.POST.get('rating'))
            review_text = request.POST.get('review_text', '').strip()

            if not (1 <= rating <= 5):
                return JsonResponse({
                    'success': False,
                    'error': 'Rating must be between 1 and 5 stars.'
                }, status=400)

            if len(review_text) < 10:
                return JsonResponse({
                    'success': False,
                    'error': 'Review must be at least 10 characters long.'
                }, status=400)

            # Update the review
            review.rating = rating
            review.review_text = review_text
            review.is_approved = False  # Re-submit for approval after edit
            review.save()

            return JsonResponse({
                'success': True,
                'message': 'Your review has been updated and is pending approval.'
            })

        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid rating value.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while updating your review.'
            }, status=500)


class DeleteReviewView(LoginRequiredMixin, View):
    """Delete a review"""

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)

        try:
            hostel_name = review.hostel.name
            review.delete()

            return JsonResponse({
                'success': True,
                'message': f'Your review for "{hostel_name}" has been deleted.'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while deleting your review.'
            }, status=500)


class ReviewModerationView(AdminRequiredMixin, ListView):
    """Admin view for moderating reviews"""
    model = Review
    template_name = 'hostels/admin/review_moderation.html'
    context_object_name = 'reviews'
    paginate_by = 20

    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'hostel').order_by('-created_at')

        status = self.request.GET.get('status')
        if status == 'pending':
            queryset = queryset.filter(is_approved=False)
        elif status == 'approved':
            queryset = queryset.filter(is_approved=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate statistics
        total_reviews = Review.objects.count()
        pending_reviews = Review.objects.filter(is_approved=False).count()
        approved_reviews = Review.objects.filter(is_approved=True).count()

        # Calculate average rating
        from django.db.models import Avg
        avg_rating = Review.objects.filter(is_approved=True).aggregate(
            avg=Avg('rating')
        )['avg'] or 0

        context['stats'] = {
            'total_reviews': total_reviews,
            'pending_reviews': pending_reviews,
            'approved_reviews': approved_reviews,
            'average_rating': avg_rating
        }

        return context


# Featured Ads System Views
class FeaturedRequestView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View for hostel owners to request featured ads"""
    model = FeaturedRequest
    form_class = FeaturedRequestForm
    template_name = 'hostels/featured/request_form.html'
    success_url = reverse_lazy('hostels:owner_dashboard')

    def test_func(self):
        return self.request.user.role == 'owner'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['hostel'] = get_object_or_404(Hostel, slug=self.kwargs['slug'], owner=self.request.user)
        return kwargs

    def form_valid(self, form):
        hostel = get_object_or_404(Hostel, slug=self.kwargs['slug'], owner=self.request.user)

        # Check if there's already a pending request for this hostel
        existing_request = FeaturedRequest.objects.filter(
            hostel=hostel,
            status='pending'
        ).first()

        if existing_request:
            messages.error(self.request, 'You already have a pending featured request for this hostel.')
            return redirect('hostels:owner_dashboard')

        form.instance.hostel = hostel
        form.instance.owner = self.request.user

        response = super().form_valid(form)
        messages.success(self.request, 'Your featured ad request has been submitted successfully! We will review it and contact you soon.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hostel = get_object_or_404(Hostel, slug=self.kwargs['slug'], owner=self.request.user)
        context['hostel'] = hostel
        context['plans'] = FeaturedPlan.objects.filter(is_active=True)
        return context


class FeaturedRequestListView(AdminRequiredMixin, ListView):
    """Admin view to list all featured requests"""
    model = FeaturedRequest
    template_name = 'hostels/admin/featured_requests.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('status')

        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('hostel', 'owner', 'plan')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        total_requests = FeaturedRequest.objects.count()
        pending_requests = FeaturedRequest.objects.filter(status='pending').count()
        approved_requests = FeaturedRequest.objects.filter(status='approved').count()
        rejected_requests = FeaturedRequest.objects.filter(status='rejected').count()

        context['stats'] = {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,
        }

        context['status_filter'] = self.request.GET.get('status', 'all')
        return context


class FeaturedRequestDetailView(AdminRequiredMixin, DetailView):
    """Admin view to review individual featured requests"""
    model = FeaturedRequest
    template_name = 'hostels/admin/featured_request_detail.html'
    context_object_name = 'request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FeaturedRequestReviewForm(instance=self.object)
        return context


class FeaturedRequestApproveView(AdminRequiredMixin, View):
    """AJAX view to approve featured requests"""

    def post(self, request, pk):
        try:
            featured_request = get_object_or_404(FeaturedRequest, pk=pk)

            if featured_request.status != 'pending':
                return JsonResponse({
                    'success': False,
                    'message': 'This request has already been processed.'
                })

            # Calculate featured period
            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(days=featured_request.plan.duration_days)

            # Update the request
            featured_request.status = 'approved'
            featured_request.reviewed_at = timezone.now()
            featured_request.reviewed_by = request.user
            featured_request.featured_start_date = start_date
            featured_request.featured_end_date = end_date
            featured_request.save()

            # Update hostel featured status
            featured_request.hostel.is_featured = True
            featured_request.hostel.save()

            # Create history record
            FeaturedHistory.objects.create(
                hostel=featured_request.hostel,
                request=featured_request,
                plan=featured_request.plan,
                start_date=start_date,
                end_date=end_date,
                amount_paid=featured_request.plan.price
            )

            return JsonResponse({
                'success': True,
                'message': f'Featured request approved! {featured_request.hostel.name} is now featured until {end_date.strftime("%Y-%m-%d %H:%M")}'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error approving request: {str(e)}'
            })


class FeaturedRequestRejectView(AdminRequiredMixin, View):
    """AJAX view to reject featured requests"""

    def post(self, request, pk):
        try:
            featured_request = get_object_or_404(FeaturedRequest, pk=pk)
            admin_notes = request.POST.get('admin_notes', '')

            if featured_request.status != 'pending':
                return JsonResponse({
                    'success': False,
                    'message': 'This request has already been processed.'
                })

            featured_request.status = 'rejected'
            featured_request.reviewed_at = timezone.now()
            featured_request.reviewed_by = request.user
            featured_request.admin_notes = admin_notes
            featured_request.save()

            return JsonResponse({
                'success': True,
                'message': 'Featured request has been rejected.'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error rejecting request: {str(e)}'
            })


class FeaturedPlansManageView(AdminRequiredMixin, ListView):
    """Admin view to manage featured pricing plans"""
    model = FeaturedPlan
    template_name = 'hostels/admin/featured_plans.html'
    context_object_name = 'plans'

    def get_queryset(self):
        """Get plans with annotated request counts"""
        from django.db.models import Count, Q
        return FeaturedPlan.objects.annotate(
            total_requests=Count('requests'),
            approved_count=Count('requests', filter=Q(requests__status='approved')),
            pending_count=Count('requests', filter=Q(requests__status='pending'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FeaturedPlanForm()
        return context


class FeaturedPlanCreateView(AdminRequiredMixin, CreateView):
    """Admin view to create new featured plans"""
    model = FeaturedPlan
    form_class = FeaturedPlanForm
    success_url = reverse_lazy('hostels:admin_featured_plans')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Featured plan "{self.object.name}" created successfully!')
        return response


class FeaturedPlanUpdateView(AdminRequiredMixin, UpdateView):
    """Admin view to update featured plans"""
    model = FeaturedPlan
    form_class = FeaturedPlanForm
    template_name = 'hostels/admin/featured_plan_form.html'
    success_url = reverse_lazy('hostels:admin_featured_plans')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate statistics for this plan
        plan = self.object
        context['approved_count'] = plan.requests.filter(status='approved').count()
        context['pending_count'] = plan.requests.filter(status='pending').count()
        context['total_revenue'] = sum(
            request.plan.price for request in plan.requests.filter(status='approved')
        )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Featured plan "{self.object.name}" updated successfully!')
        return response


class CheckFeaturedStatusView(View):
    """Background task view to check and update featured status"""

    def get(self, request):
        """Check for expired featured periods and update hostel status"""
        from django.utils import timezone

        # Find expired featured requests
        expired_requests = FeaturedRequest.objects.filter(
            status='approved',
            featured_end_date__lt=timezone.now()
        )

        updated_count = 0
        for req in expired_requests:
            req.status = 'expired'
            req.save()

            # Check if hostel has other active featured periods
            active_requests = FeaturedRequest.objects.filter(
                hostel=req.hostel,
                status='approved',
                featured_start_date__lte=timezone.now(),
                featured_end_date__gte=timezone.now()
            )

            if not active_requests.exists():
                req.hostel.is_featured = False
                req.hostel.save()

            updated_count += 1

        return JsonResponse({
            'success': True,
            'updated_count': updated_count,
            'message': f'Updated {updated_count} expired featured periods'
        })
