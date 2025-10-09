from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views

app_name = 'hostels'

urlpatterns = [
    # Home and listing pages
    path('', views.HomeView.as_view(), name='home'),
    path('hostels/', views.HostelListView.as_view(), name='hostel_list'),
    path('hostels/<slug:slug>/', views.HostelDetailView.as_view(), name='hostel_detail'),
    path('hostels/<slug:slug>/contact/', views.RevealContactView.as_view(), name='reveal_contact'),

    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # path('verify-email/<uuid:token>/', views.VerifyEmailView.as_view(), name='verify_email'),

    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='hostels/auth/password_reset.html',
        email_template_name='hostels/auth/password_reset_email.html',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='hostels/auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='hostels/auth/password_reset_confirm.html',
        success_url='/password-reset-complete/'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='hostels/auth/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Dashboard
    # path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # CRUD Operations for Items
    # path('items/', views.ItemListView.as_view(), name='item_list'),
    # path('items/create/', views.ItemCreateView.as_view(), name='item_create'),
    # path('items/<slug:slug>/', views.ItemDetailView.as_view(), name='item_detail'),
    # path('items/<slug:slug>/edit/', views.ItemUpdateView.as_view(), name='item_update'),
    # path('items/<slug:slug>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),

    # Static pages
    path('help/', views.HelpCenterView.as_view(), name='help_center'),
    path('contact/', views.ContactUsView.as_view(), name='contact_us'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path('search-location/', views.SearchByLocationView.as_view(), name='search_by_location'),
    path('reviews/', views.ReviewsListView.as_view(), name='reviews_list'),

    # Owner dashboard
    path('owner-dashboard/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('owner-dashboard/hostel/add/', views.AddHostelView.as_view(), name='add_hostel'),
    path('owner-dashboard/hostel/<slug:slug>/edit/', views.EditHostelView.as_view(), name='edit_hostel'),
    path('owner-dashboard/hostel/<slug:slug>/delete/', views.DeleteHostelView.as_view(), name='delete_hostel'),

    # Student features
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('favorites/add/<slug:slug>/', views.AddToFavoritesView.as_view(), name='add_to_favorites'),
    path('favorites/remove/<slug:slug>/', views.RemoveFromFavoritesView.as_view(), name='remove_from_favorites'),

    # Review system
    path('reviews/add/<slug:slug>/', views.AddReviewView.as_view(), name='add_review'),
    path('reviews/<int:review_id>/edit/', views.UpdateReviewView.as_view(), name='update_review'),
    path('reviews/<int:review_id>/delete/', views.DeleteReviewView.as_view(), name='delete_review'),

    # Report system
    path('report/<slug:slug>/', views.ReportHostelView.as_view(), name='report_hostel'),
    path('api/resolve-report/<int:report_id>/', views.ResolveReportView.as_view(), name='resolve_report'),
    path('api/delete-report/<int:report_id>/', views.DeleteReportView.as_view(), name='delete_report'),

    # Admin features
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/hostels/', views.AdminHostelListView.as_view(), name='admin_hostels'),
    path('admin-dashboard/hostels/pending/', views.PendingHostelsView.as_view(), name='pending_hostels'),
    path('admin-dashboard/users/', views.AdminUserListView.as_view(), name='admin_users'),
    path('admin-dashboard/reviews/', views.ReviewModerationView.as_view(), name='admin_reviews'),
    path('admin-dashboard/analytics/', views.AdminAnalyticsView.as_view(), name='admin_analytics'),
    path('admin-dashboard/reports/', views.ReportsView.as_view(), name='reports'),
    path('admin-dashboard/export/', admin_views.ExportDataView.as_view(), name='export_data'),

    # Featured ads system
    path('featured/request/<slug:slug>/', views.FeaturedRequestView.as_view(), name='request_featured'),
    path('admin-dashboard/featured/requests/', views.FeaturedRequestListView.as_view(), name='admin_featured_requests'),
    path('admin-dashboard/featured/request/<int:pk>/', views.FeaturedRequestDetailView.as_view(), name='admin_featured_request_detail'),
    path('admin-dashboard/featured/plans/', views.FeaturedPlansManageView.as_view(), name='admin_featured_plans'),
    path('admin-dashboard/featured/plans/create/', views.FeaturedPlanCreateView.as_view(), name='create_featured_plan'),
    path('admin-dashboard/featured/plans/<int:pk>/edit/', views.FeaturedPlanUpdateView.as_view(), name='edit_featured_plan'),

    # Notifications
    # path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    # path('notifications/mark-read/<int:pk>/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),

    # API endpoints for AJAX requests
    path('api/geocode/', views.GeocodeView.as_view(), name='geocode'),
    path('api/search/', views.SearchAPIView.as_view(), name='search_api'),

    # Admin API endpoints
    path('api/admin/approve-hostel/<uuid:hostel_id>/',
         admin_views.ApproveHostelView.as_view(),
         name='approve_hostel'),
    path('api/admin/reject-hostel/<uuid:hostel_id>/',
         admin_views.RejectHostelView.as_view(),
         name='reject_hostel'),
    path('api/admin/toggle-featured/<uuid:hostel_id>/',
         admin_views.ToggleFeaturedView.as_view(),
         name='toggle_featured'),
    path('api/admin/toggle-active/<uuid:hostel_id>/',
         admin_views.ToggleActiveView.as_view(),
         name='toggle_active'),
    path('api/admin/bulk-action/',
         admin_views.BulkHostelActionView.as_view(),
         name='bulk_hostel_action'),
    path('api/admin/bulk-user-action/',
         admin_views.BulkUserActionView.as_view(),
         name='bulk_user_action'),
    path('api/admin/delete-hostel/<uuid:hostel_id>/',
         admin_views.DeleteHostelView.as_view(),
         name='delete_hostel'),
    path('api/admin/delete-user/<uuid:user_id>/',
         admin_views.DeleteUserView.as_view(),
         name='delete_user'),
    path('admin-dashboard/backup/',
         admin_views.SystemBackupView.as_view(),
         name='system_backup'),

    # Review moderation API endpoints
    path('api/admin/approve-review/<int:review_id>/',
         admin_views.ApproveReviewView.as_view(),
         name='approve_review'),
    path('api/admin/unapprove-review/<int:review_id>/',
         admin_views.UnapproveReviewView.as_view(),
         name='unapprove_review'),
    path('api/admin/delete-review/<int:review_id>/',
         admin_views.DeleteReviewAdminView.as_view(),
         name='delete_review_admin'),

    # Featured ads API endpoints
    path('api/admin/approve-featured/<int:pk>/', views.FeaturedRequestApproveView.as_view(), name='approve_featured_request'),
    path('api/admin/reject-featured/<int:pk>/', views.FeaturedRequestRejectView.as_view(), name='reject_featured_request'),
    path('api/check-featured-status/', views.CheckFeaturedStatusView.as_view(), name='check_featured_status'),

    # path('api/', include('hostels.api_urls')),  # DRF API urls
]
