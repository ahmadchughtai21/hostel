from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Hostel, Facility, HostelFacility, RoomType,
    HostelImage, ContactReveal, HostelView, Favorite, Review, Report, HostelSubscription
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('role', 'phone_number', 'whatsapp_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile Info', {'fields': ('role', 'phone_number', 'whatsapp_number')}),
    )


class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1


class HostelImageInline(admin.TabularInline):
    model = HostelImage
    extra = 1


class HostelFacilityInline(admin.TabularInline):
    model = HostelFacility
    extra = 1


class HostelSubscriptionInline(admin.StackedInline):
    model = HostelSubscription
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Subscription Details', {
            'fields': ('monthly_fee', 'status', 'subscription_start_date', 'subscription_end_date')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_reference', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'owner', 'is_featured', 'is_verified', 'is_active',
        'nearby_landmark', 'landmark_distance', 'subscription_status', 'min_price', 'created_at'
    )
    list_filter = ('is_featured', 'is_verified', 'is_active', 'created_at')
    search_fields = ('name', 'address', 'nearby_landmark', 'owner__username')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [RoomTypeInline, HostelImageInline, HostelFacilityInline, HostelSubscriptionInline]
    actions = ['mark_verified', 'mark_unverified', 'mark_featured', 'mark_unfeatured']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'owner', 'description')
        }),
        ('Location Details', {
            'fields': ('address', 'latitude', 'longitude', 'google_location_link')
        }),
        ('Landmark Information', {
            'fields': ('nearby_landmark', 'landmark_distance'),
            'description': 'Specify nearby universities, schools, or workplaces to help students find relevant accommodations.'
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'whatsapp_number')
        }),
        ('Status & Settings', {
            'fields': ('is_featured', 'is_verified', 'is_active'),
            'description': 'Featured hostels appear first in search results and on the homepage.'
        }),
    )

    def subscription_status(self, obj):
        try:
            return obj.subscription.get_status_display()
        except HostelSubscription.DoesNotExist:
            return 'No subscription'
    subscription_status.short_description = 'Subscription'

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_verified.short_description = "Mark selected hostels as verified"

    def mark_unverified(self, request, queryset):
        queryset.update(is_verified=False)
    mark_unverified.short_description = "Mark selected hostels as unverified"

    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_featured.short_description = "Mark selected hostels as featured"

    def mark_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)
    mark_unfeatured.short_description = "Remove featured status from selected hostels"


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'created_at')
    search_fields = ('name',)


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'type', 'price', 'available_rooms')
    list_filter = ('type', 'price')
    search_fields = ('hostel__name',)


@admin.register(HostelImage)
class HostelImageAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')


@admin.register(ContactReveal)
class ContactRevealAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'user', 'ip_address', 'timestamp')
    list_filter = ('timestamp',)
    readonly_fields = ('timestamp',)


@admin.register(HostelView)
class HostelViewAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'user', 'ip_address', 'timestamp')
    list_filter = ('timestamp', 'hostel')
    readonly_fields = ('timestamp',)
    search_fields = ('hostel__name', 'user__username', 'ip_address')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'hostel', 'created_at')
    list_filter = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = "Disapprove selected reviews"


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'reporter', 'report_type', 'is_resolved', 'created_at')
    list_filter = ('report_type', 'is_resolved', 'created_at')
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_resolved.short_description = "Mark selected reports as resolved"


@admin.register(HostelSubscription)
class HostelSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'hostel', 'status', 'monthly_fee', 'subscription_start_date',
        'subscription_end_date', 'days_until_expiry', 'created_at'
    )
    list_filter = ('status', 'created_at', 'subscription_start_date', 'subscription_end_date')
    search_fields = ('hostel__name', 'payment_reference', 'payment_method')
    readonly_fields = ('created_at', 'updated_at', 'days_until_expiry', 'is_active')
    actions = ['activate_subscriptions', 'expire_subscriptions']

    fieldsets = (
        ('Hostel Information', {
            'fields': ('hostel',)
        }),
        ('Subscription Details', {
            'fields': ('monthly_fee', 'status', 'subscription_start_date', 'subscription_end_date')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_reference')
        }),
        ('Status Information', {
            'fields': ('is_active', 'days_until_expiry'),
            'classes': ('collapse',)
        }),
        ('Notes & Administration', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def activate_subscriptions(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f'{queryset.count()} subscriptions activated.')
    activate_subscriptions.short_description = "Activate selected subscriptions"

    def expire_subscriptions(self, request, queryset):
        queryset.update(status='expired')
        self.message_user(request, f'{queryset.count()} subscriptions expired.')
    expire_subscriptions.short_description = "Mark selected subscriptions as expired"
