from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from crispy_forms.bootstrap import FormActions

from .models import Hostel, RoomType, HostelImage, Review, Report, Item, Category, Facility, HostelFacility, FeaturedPlan, FeaturedRequest

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='student')
    phone_number = forms.CharField(max_length=20, required=False)
    whatsapp_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'phone_number', 'whatsapp_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'role',
            Row(
                Column('phone_number', css_class='form-group col-md-6 mb-0'),
                Column('whatsapp_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Register', css_class='btn-primary btn-lg btn-block')
            )
        )


class UserProfileForm(forms.ModelForm):
    """User profile update form"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'whatsapp_number', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'email',
            Row(
                Column('phone_number', css_class='form-group col-md-6 mb-0'),
                Column('whatsapp_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Update Profile', css_class='btn-primary')
            )
        )


class HostelForm(forms.ModelForm):
    """Form for adding/editing hostels"""
    facilities = forms.ModelMultipleChoiceField(
        queryset=Facility.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select all facilities available at your hostel"
    )
    new_facility = forms.CharField(
        max_length=100,
        required=False,
        help_text="Add a new facility if not listed above"
    )

    class Meta:
        model = Hostel
        fields = (
            'name', 'address', 'google_location_link', 'nearby_landmark',
            'landmark_distance', 'description', 'gender_type', 'contact_email',
            'contact_phone', 'whatsapp_number'
        )
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'Enter hostel name'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'Enter complete address with landmarks'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'Describe your hostel, amenities, rules, and atmosphere'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'your.email@example.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': '+92300123456'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': '+92300123456 (optional)'
            }),
            'google_location_link': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'https://maps.google.com/... (optional)'
            }),
            'nearby_landmark': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'e.g., FAST University, LUMS, UMT, COMSATS'
            }),
            'landmark_distance': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': '0.5',
                'step': '0.1',
                'min': '0'
            }),
            'gender_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set initial facilities if editing existing hostel
        if self.instance.pk:
            self.fields['facilities'].initial = self.instance.hostel_facilities.all().values_list('facility', flat=True)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'address',
            'google_location_link',
            Row(
                Column('nearby_landmark', css_class='form-group col-md-8 mb-0'),
                Column('landmark_distance', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'description',
            Row(
                Column('contact_email', css_class='form-group col-md-6 mb-0'),
                Column('contact_phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'whatsapp_number',
            FormActions(
                Submit('submit', 'Save Hostel', css_class='btn-primary')
            )
        )

    def save(self, commit=True):
        hostel = super().save(commit)

        if commit:
            # Handle facilities
            selected_facilities = self.cleaned_data.get('facilities', [])
            new_facility_name = self.cleaned_data.get('new_facility')

            # Clear existing facilities
            hostel.hostel_facilities.all().delete()

            # Add selected facilities
            for facility in selected_facilities:
                HostelFacility.objects.create(hostel=hostel, facility=facility)

            # Add new facility if provided
            if new_facility_name:
                new_facility, created = Facility.objects.get_or_create(
                    name=new_facility_name.strip()
                )
                HostelFacility.objects.get_or_create(hostel=hostel, facility=new_facility)

        return hostel


class HostelImageForm(forms.ModelForm):
    """Form for uploading hostel images"""

    class Meta:
        model = HostelImage
        fields = ('image', 'caption', 'is_primary')
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Optional caption for this image'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({
            'accept': 'image/*',
            'class': 'form-control'
        })


# Form set for multiple images
HostelImageFormSet = forms.inlineformset_factory(
    Hostel,
    HostelImage,
    form=HostelImageForm,
    extra=3,  # Allow 3 extra forms
    can_delete=True,
    min_num=0,  # Make all forms optional
    validate_min=False
)


class RoomTypeForm(forms.ModelForm):
    """Form for adding room types"""

    class Meta:
        model = RoomType
        fields = ('type', 'price', 'description', 'available_rooms')
        widgets = {
            'type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': '100',
                'min': '0',
                'step': '0.01'
            }),
            'available_rooms': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': '10',
                'min': '1'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'Describe this room type'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('type', css_class='form-group col-md-6 mb-0'),
                Column('price', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'available_rooms',
            'description',
            FormActions(
                Submit('submit', 'Add Room Type', css_class='btn-primary')
            )
        )


# We'll define this after RoomTypeForm is created


class HostelImageForm(forms.ModelForm):
    """Form for uploading hostel images"""

    class Meta:
        model = HostelImage
        fields = ('image', 'caption', 'is_primary')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'image',
            'caption',
            'is_primary',
            FormActions(
                Submit('submit', 'Upload Image', css_class='btn-primary')
            )
        )


class ReviewForm(forms.ModelForm):
    """Form for adding reviews"""

    class Meta:
        model = Review
        fields = ('rating', 'review_text')
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'review_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'rating',
            'review_text',
            FormActions(
                Submit('submit', 'Submit Review', css_class='btn-primary')
            )
        )


class ReportForm(forms.ModelForm):
    """Form for reporting hostels"""

    class Meta:
        model = Report
        fields = ('report_type', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the issue...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'report_type',
            'description',
            FormActions(
                Submit('submit', 'Submit Report', css_class='btn-danger')
            )
        )


class HostelSearchForm(forms.Form):
    """Form for searching and filtering hostels"""
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search hostels or locations...',
            'class': 'form-control'
        })
    )
    landmark = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Near university, school, or workplace...',
            'class': 'form-control'
        })
    )
    max_distance = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max distance (km)',
            'step': '0.5',
            'min': '0'
        })
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Price (PKR)'})
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Max Price (PKR)'})
    )
    room_type = forms.ChoiceField(
        choices=[('', 'Any Room Type')] + RoomType.ROOM_TYPE_CHOICES,
        required=False
    )
    gender_type = forms.ChoiceField(
        choices=[('', 'Any Gender')] + Hostel.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    facilities = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    sort = forms.ChoiceField(
        choices=[
            ('featured', 'Featured First'),
            ('newest', 'Newest First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('distance', 'Distance'),
            ('rating', 'Highest Rated'),
        ],
        required=False,
        initial='featured'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Facility
        self.fields['facilities'].queryset = Facility.objects.all()

        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            'q',
            Row(
                Column('min_price', css_class='form-group col-md-6 mb-0'),
                Column('max_price', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'room_type',
            'facilities',
            'sort',
            FormActions(
                Submit('submit', 'Search', css_class='btn-primary')
            )
        )


class ItemForm(forms.ModelForm):
    """Form for CRUD operations on items"""

    class Meta:
        model = Item
        fields = ('title', 'description', 'category', 'image', 'price')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'category',
            'description',
            Row(
                Column('price', css_class='form-group col-md-6 mb-0'),
                Column('image', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Save Item', css_class='btn-primary')
            )
        )


class CategoryForm(forms.ModelForm):
    """Form for managing categories"""

    class Meta:
        model = Category
        fields = ('name', 'description', 'icon')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'icon',
            'description',
            FormActions(
                Submit('submit', 'Save Category', css_class='btn-primary')
            )
        )


class SearchForm(forms.Form):
    """Advanced search form for items"""

    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search items...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Price (PKR)', 'step': '0.01'})
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Max Price (PKR)', 'step': '0.01'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('newest', 'Newest First'),
            ('oldest', 'Oldest First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('title', 'Title A-Z'),
        ],
        required=False,
        initial='newest'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            'q',
            Row(
                Column('category', css_class='form-group col-md-6 mb-0'),
                Column('sort_by', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('min_price', css_class='form-group col-md-6 mb-0'),
                Column('max_price', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Search', css_class='btn-primary')
            )
        )


# Form set for multiple room types
RoomTypeFormSet = forms.inlineformset_factory(
    Hostel,
    RoomType,
    form=RoomTypeForm,
    extra=2,  # Allow 2 extra forms
    can_delete=True,
    min_num=0,  # Make all forms optional
    validate_min=False
)


class FeaturedRequestForm(forms.ModelForm):
    """Form for hostel owners to request featured ads"""

    class Meta:
        model = FeaturedRequest
        fields = [
            'plan', 'contact_name', 'contact_phone', 'contact_email',
            'whatsapp_number', 'payment_method', 'payment_reference',
            'payment_screenshot'
        ]
        widgets = {
            'contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+92 300 1234567'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+92 300 1234567 (optional)'
            }),
            'payment_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank transfer, JazzCash, EasyPaisa, etc.'
            }),
            'payment_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Transaction ID or reference number'
            }),
            'payment_screenshot': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf'
            }),
            'plan': forms.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.hostel = kwargs.pop('hostel', None)
        super().__init__(*args, **kwargs)

        # Filter active plans only
        self.fields['plan'].queryset = FeaturedPlan.objects.filter(is_active=True)

        # Pre-populate contact info if user provided
        if self.user:
            self.fields['contact_name'].initial = self.user.get_full_name() or self.user.username
            self.fields['contact_email'].initial = self.user.email
            if hasattr(self.user, 'phone_number'):
                self.fields['contact_phone'].initial = self.user.phone_number
            if hasattr(self.user, 'whatsapp_number'):
                self.fields['whatsapp_number'].initial = self.user.whatsapp_number

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('plan', template='hostels/forms/plan_radio_select.html'),
            Row(
                Column('contact_name', css_class='form-group col-md-6 mb-0'),
                Column('contact_email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('contact_phone', css_class='form-group col-md-6 mb-0'),
                Column('whatsapp_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('payment_method', css_class='form-group col-md-6 mb-0'),
                Column('payment_reference', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'payment_screenshot',
            FormActions(
                Submit('submit', 'Submit Featured Request', css_class='btn-primary btn-lg')
            )
        )

    def clean_payment_screenshot(self):
        screenshot = self.cleaned_data.get('payment_screenshot')
        if screenshot:
            if screenshot.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be under 5MB.")
        return screenshot


class FeaturedPlanForm(forms.ModelForm):
    """Form for admin to manage featured plans"""

    class Meta:
        model = FeaturedPlan
        fields = ['name', 'duration_type', 'duration_days', 'price', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_type': forms.Select(attrs={'class': 'form-control'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('duration_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('duration_days', css_class='form-group col-md-6 mb-0'),
                Column('price', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            'is_active',
            FormActions(
                Submit('submit', 'Save Plan', css_class='btn-primary')
            )
        )


class FeaturedRequestReviewForm(forms.ModelForm):
    """Form for admin to review and approve/reject featured requests"""

    class Meta:
        model = FeaturedRequest
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'status',
            'admin_notes',
            FormActions(
                Submit('submit', 'Update Request', css_class='btn-primary')
            )
        )
