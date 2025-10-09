from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
import uuid
from decimal import Decimal


class User(AbstractUser):
    """Extended User model with roles"""
    ROLE_CHOICES = [
        ('owner', 'Hostel Owner'),
        ('student', 'Student/Client'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Hostel(models.Model):
    """Main hostel model"""
    GENDER_CHOICES = [
        ('male', 'Boys/Men Only'),
        ('female', 'Girls/Women Only'),
        ('mixed', 'Co-ed/Mixed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hostels')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_location_link = models.URLField(max_length=500, blank=True, help_text="Google Maps location link")
    gender_type = models.CharField(max_length=10, choices=GENDER_CHOICES, default='mixed', help_text="Who can stay at this hostel")

    # Landmark proximity information
    nearby_landmark = models.CharField(max_length=300, blank=True, help_text="Name of nearby university, school, or workplace")
    landmark_distance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Distance from landmark in kilometers")

    description = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Featured hostels appear first in search results and on homepage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['is_verified', 'is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['landmark_distance']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('hostels:hostel_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    @property
    def min_price(self):
        """Get the minimum room price for this hostel"""
        min_room = self.room_types.order_by('price').first()
        return min_room.price if min_room else None

    @property
    def contact_reveals_count(self):
        """Count how many times contact info was revealed"""
        return self.contact_reveals.count()

    @property
    def views_count(self):
        """Count how many times hostel was viewed"""
        return self.views.count()

    @property
    def current_featured_request(self):
        """Get current active featured request if any"""
        from django.utils import timezone
        return self.featured_requests.filter(
            status='approved',
            featured_start_date__lte=timezone.now(),
            featured_end_date__gte=timezone.now()
        ).first()

    @property
    def is_currently_featured(self):
        """Check if hostel is currently featured based on active requests"""
        return self.current_featured_request is not None

    @property
    def featured_until(self):
        """Get the end date of current featured period"""
        current = self.current_featured_request
        return current.featured_end_date if current else None

    @property
    def average_rating(self):
        """Calculate average rating from approved reviews"""
        approved_reviews = self.reviews.filter(is_approved=True)
        if approved_reviews.exists():
            total_rating = sum(review.rating for review in approved_reviews)
            return round(total_rating / approved_reviews.count(), 1)
        return 0

    @property
    def rating_count(self):
        """Get count of approved reviews"""
        return self.reviews.filter(is_approved=True).count()

    @property
    def rating_distribution(self):
        """Get distribution of ratings (1-5 stars)"""
        approved_reviews = self.reviews.filter(is_approved=True)
        distribution = {}
        for i in range(1, 6):
            distribution[i] = approved_reviews.filter(rating=i).count()
        return distribution

    @property
    def rating_stars_display(self):
        """Get rating as filled/empty stars for display"""
        from django.utils.safestring import mark_safe
        avg_rating = self.average_rating
        stars_html = []
        for i in range(1, 6):
            if i <= avg_rating:
                stars_html.append('<i class="fas fa-star"></i>')  # filled star
            elif i - 0.5 <= avg_rating:
                stars_html.append('<i class="fas fa-star-half-alt"></i>')  # half star
            else:
                stars_html.append('<i class="far fa-star"></i>')  # empty star
        return mark_safe(''.join(stars_html))


class Facility(models.Model):
    """Available facilities for hostels"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # CSS icon class
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "facilities"
        ordering = ['name']

    def __str__(self):
        return self.name


class HostelFacility(models.Model):
    """Many-to-many relationship between hostels and facilities"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='hostel_facilities')
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='hostel_facilities')

    class Meta:
        unique_together = ('hostel', 'facility')

    def __str__(self):
        return f"{self.hostel.name} - {self.facility.name}"


class RoomType(models.Model):
    """Room types available in a hostel"""
    ROOM_TYPE_CHOICES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('shared', 'Shared Room'),
        ('dormitory', 'Dormitory'),
    ]

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='room_types')
    type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    available_rooms = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('hostel', 'type')
        indexes = [
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return f"{self.hostel.name} - {self.get_type_display()} (₨{self.price})"


class HostelImage(models.Model):
    """Images for hostels"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hostel_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.hostel.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per hostel
        if self.is_primary:
            HostelImage.objects.filter(hostel=self.hostel, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class ContactReveal(models.Model):
    """Track when contact information is revealed"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='contact_reveals')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hostel.name} - Contact revealed at {self.timestamp}"


class HostelView(models.Model):
    """Track hostel page views"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hostel View"
        verbose_name_plural = "Hostel Views"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.hostel.name} - Viewed at {self.timestamp}"


class Favorite(models.Model):
    """User favorites/wishlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'hostel')

    def __str__(self):
        return f"{self.user.username} - {self.hostel.name}"


class Review(models.Model):
    """Hostel reviews (optional feature)"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hostel', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.hostel.name} - {self.rating} stars by {self.user.username}"


class Report(models.Model):
    """Reports for fake/inappropriate hostels"""
    REPORT_TYPES = [
        ('fake', 'Fake Information'),
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('other', 'Other'),
    ]

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_resolved')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report on {self.hostel.name} - {self.get_report_type_display()}"


class Category(models.Model):
    """Categories for items"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Item(models.Model):
    """General purpose item model for CRUD operations"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(
        upload_to='item_images/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'category']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:8]}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('hostels:item_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class Notification(models.Model):
    """Notification system"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class EmailVerification(models.Model):
    """Email verification tokens"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Email verification for {self.user.username}"

    @property
    def is_expired(self):
        """Check if verification token is expired (24 hours)"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(hours=24)


class HostelSubscription(models.Model):
    """Track hostel subscription and payment status"""
    SUBSCRIPTION_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    hostel = models.OneToOneField(Hostel, on_delete=models.CASCADE, related_name='subscription')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('8999.00'), help_text="Monthly subscription fee (PKR)")
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default='pending')
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=100, blank=True, help_text="External payment method used")
    payment_reference = models.CharField(max_length=200, blank=True, help_text="External payment reference/transaction ID")
    notes = models.TextField(blank=True, help_text="Admin notes about payment status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostel.name} - {self.get_status_display()}"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        from django.utils import timezone
        if self.status == 'active' and self.subscription_end_date:
            return timezone.now().date() <= self.subscription_end_date
        return False

    @property
    def days_until_expiry(self):
        """Get days until subscription expires"""
        if self.subscription_end_date:
            from django.utils import timezone
            delta = self.subscription_end_date - timezone.now().date()
            return delta.days
        return None


class FeaturedPlan(models.Model):
    """Pricing plans for featured ads"""
    DURATION_CHOICES = [
        ('1_day', '1 Day'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
    ]

    name = models.CharField(max_length=50, unique=True)
    duration_type = models.CharField(max_length=20, choices=DURATION_CHOICES, unique=True)
    duration_days = models.IntegerField(help_text="Number of days for this plan")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in PKR")
    description = models.TextField(blank=True, help_text="Benefits and features of this plan")
    is_active = models.BooleanField(default=True, help_text="Whether this plan is available for purchase")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['duration_days']

    def __str__(self):
        return f"{self.name} - PKR {self.price}"

    @property
    def duration_display(self):
        """Human readable duration"""
        if self.duration_days == 1:
            return "1 Day"
        elif self.duration_days == 7:
            return "1 Week"
        elif self.duration_days == 30:
            return "1 Month"
        else:
            return f"{self.duration_days} Days"


class FeaturedRequest(models.Model):
    """Track requests from hostel owners for featured ads"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved & Active'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='featured_requests')
    plan = models.ForeignKey(FeaturedPlan, on_delete=models.CASCADE, related_name='requests')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='featured_requests')

    # Contact and payment info
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    whatsapp_number = models.CharField(max_length=20, blank=True)
    payment_method = models.CharField(max_length=100, blank=True, help_text="How payment was made")
    payment_reference = models.CharField(max_length=200, blank=True, help_text="Transaction ID or reference")
    payment_screenshot = models.ImageField(
        upload_to='payment_screenshots/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
        help_text="Screenshot or receipt of payment"
    )

    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_featured_requests')

    # Featured period (set when approved)
    featured_start_date = models.DateTimeField(null=True, blank=True)
    featured_end_date = models.DateTimeField(null=True, blank=True)

    # Admin notes
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes")

    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['featured_start_date', 'featured_end_date']),
        ]

    def __str__(self):
        return f"{self.hostel.name} - {self.plan.name} ({self.get_status_display()})"

    @property
    def is_active(self):
        """Check if featured period is currently active"""
        from django.utils import timezone
        if self.status == 'approved' and self.featured_start_date and self.featured_end_date:
            now = timezone.now()
            return self.featured_start_date <= now <= self.featured_end_date
        return False

    @property
    def days_remaining(self):
        """Get days remaining in featured period"""
        if self.featured_end_date:
            from django.utils import timezone
            delta = self.featured_end_date - timezone.now()
            return max(0, delta.days)
        return 0

    @property
    def total_amount(self):
        """Get the total amount for this request"""
        return self.plan.price


class FeaturedHistory(models.Model):
    """Track history of featured periods for analytics"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='featured_history')
    request = models.OneToOneField(FeaturedRequest, on_delete=models.CASCADE, related_name='history')
    plan = models.ForeignKey(FeaturedPlan, on_delete=models.CASCADE)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    # Performance metrics
    views_during_period = models.IntegerField(default=0)
    contacts_revealed_during_period = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Featured histories"

    def __str__(self):
        return f"{self.hostel.name} - Featured {self.start_date.date()} to {self.end_date.date()}"
