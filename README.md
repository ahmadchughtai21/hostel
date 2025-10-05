# HostelHub - Hostel Listing & Discovery Platform

A full-stack Django web application for hostel listing and discovery, connecting students with verified hostel owners.

## 🚀 Features

### 👨‍💼 Hostel Owner Features
- Register/login/logout with Django Auth
- Profile management (name, phone, WhatsApp/email)
- Add multiple hostels with:
  - Name, address, auto-geocoding to lat/lon
  - Room types with pricing
  - Facilities (Wi-Fi, meals, AC, etc.)
  - Multiple images
  - Contact details
- Edit/delete listings
- Dashboard with analytics (contact button clicks, views)

### 👩 Student/Client Features
- Browse/search hostels
- Advanced filters: price range, facilities, distance, room type
- Sort by: price (low/high), distance, ratings
- Detailed hostel pages with photos, facilities, pricing
- "Show Contact" button with tracking
- Favorites/wishlist system (requires login)
- Mobile-optimized responsive design

### 👨‍💻 Admin Features
- Approve/verify hostel listings
- Manage users (owners/students)
- Admin dashboard with comprehensive stats
- Handle reports/flags for inappropriate content

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6 (Python)
- **Frontend**: Django Templates + Tailwind CSS
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Authentication**: Django built-in auth system
- **Forms**: Django Crispy Forms with Tailwind
- **Maps**: Google Maps API integration (configured)
- **Storage**: Local filesystem (dev) / AWS S3 (production ready)

## 📋 Database Schema

### Core Models:
- **User** (Extended Django User): roles (owner/student/admin), contact info
- **Hostel**: main hostel information with geocoding
- **RoomType**: different room types and pricing per hostel
- **Facility**: available facilities (Wi-Fi, AC, meals, etc.)
- **HostelFacility**: many-to-many relationship between hostels and facilities
- **HostelImage**: multiple images per hostel with primary image selection
- **ContactReveal**: tracking when contact info is revealed
- **Favorite**: user favorites/wishlist
- **Review**: hostel reviews and ratings (optional)
- **Report**: reporting system for inappropriate content

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (included)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd hostel
   ```

2. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies** (already installed):
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations** (already done):
   ```bash
   python manage.py migrate
   ```

5. **Create superuser** (already created):
   ```bash
   python manage.py createsuperuser
   # Default: admin / admin@hostel.com / admin123
   ```

6. **Start development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 🎨 Frontend Features

### Mobile-First Design
- Responsive Tailwind CSS framework
- Clean, modern UI components
- Optimized for mobile devices

### Key Pages
- **Home**: Hero section with search, featured hostels
- **Hostel List**: Grid/list view with advanced filters
- **Hostel Detail**: Comprehensive hostel information
- **Auth Pages**: Login, register, profile management
- **Owner Dashboard**: Hostel management and analytics
- **Admin Dashboard**: System administration

### Components
- Navigation bar with search
- Hostel cards with facilities
- Contact reveal modal
- Filter sidebar
- Pagination
- Messages/alerts system

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production:

```env
# Database (Production)
DB_NAME=hostel_db
DB_USER=hostel_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Google Maps API
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# AWS S3 (Production)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name

# Security
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

### Database Configuration

**Development (Current)**: SQLite
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Production**: PostgreSQL/MySQL (portable)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # or mysql
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```

## 📱 API Endpoints

- `/api/geocode/` - Address geocoding
- `/api/search/` - Hostel search autocomplete
- `/hostels/<slug>/contact/` - Contact reveal tracking

## 🎯 Best Practices Implemented

- **Django CBVs**: Class-based views for clean code organization
- **Django ORM**: Database-agnostic queries
- **SEO-friendly URLs**: Slug-based hostel URLs
- **Form Validation**: Crispy forms with Tailwind styling
- **Image Optimization**: Pillow integration
- **Pagination**: Efficient hostel listing pagination
- **Security**: CSRF protection, user authentication
- **Database Indexing**: Optimized queries for lat/lon and price
- **Responsive Design**: Mobile-first approach

## 🚀 Future Enhancements

- **API Development**: Django REST Framework for mobile apps
- **Advanced Search**: Elasticsearch integration
- **Cloud Storage**: S3/DigitalOcean Spaces for media files
- **Caching**: Redis implementation for performance
- **Real-time Features**: WebSocket integration
- **Payment Integration**: Stripe/PayPal for bookings
- **Microservices**: Scalable architecture

## 📞 Support

For issues or questions:
1. Check the Django admin panel for data management
2. Review logs in the console
3. Check database migrations: `python manage.py showmigrations`
4. Run system checks: `python manage.py check`

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests: `python manage.py test`
4. Submit pull request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using Django & Tailwind CSS**
