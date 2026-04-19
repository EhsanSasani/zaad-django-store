ZAAD – Django Catalog Website
=================================

Overview
--------
ZAAD is a catalog-based website built with Django.
This version is focused on product presentation and daily admin updates.
There is no shopping cart, authentication system, or payment integration.
The admin panel is the primary interface for managing content.

The project is designed to:
- Display categorized products (Flowers, Bakery, Gifts)
- Be SEO-friendly
- Support dark/light theme
- Be easily deployable
- Be extendable in future phases (cart, auth, payments)


Tech Stack
----------
- Python (Tested with 3.12+)
- Django (Tested with 5.x)
- SQLite (Development)
- PostgreSQL (Recommended for Production)
- Bootstrap (UI base)
- Custom CSS Design System


Project Structure
-----------------
config/
    settings.py
    urls.py
main/
    models.py
    views.py
    admin.py
    urls.py
    templates/
    static/
        css/
        js/
        images/
media/
    product images


Core Features
-------------
1. Catalog Display
   - Product base model
   - Category-based filtering
   - Detail pages
   - SEO-friendly URLs

2. Admin Workflow
   - Admin creates and edits products daily
   - Image upload via Django admin
   - Simple content management
   - No frontend editing

3. SEO
   - JSON-LD structured data
   - Canonical URLs
   - Sitemap support
   - Robots.txt ready
   - Clean slug-based URLs

4. UI/UX
   - Minimal premium style
   - Dark / Light mode toggle
   - Responsive layout
   - Optimized hero sections


Database Design
---------------
Base Model:
- Product (abstract or shared logic base)

Derived Models:
- Flower
- BakeryItem
- GiftItem

Each product includes:
- title
- slug
- description
- price (optional in current version)
- image
- created_at
- updated_at
- is_active


Environment Variables
---------------------
Required:
- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS

Optional (Branding / Analytics):
- GOOGLE_ANALYTICS_ID
- SITE_NAME
- CONTACT_EMAIL

Example .env:

SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
SITE_NAME=ZAAD
CONTACT_EMAIL=info@example.com


Static & Media
--------------
Development:
- STATIC_URL is configured
- Media files stored locally

Production:
- Define STATIC_ROOT
- Run:
  python manage.py collectstatic
- Use proper media storage (recommended: cloud storage)


Deployment Notes
----------------
Basic Production Checklist:
1. Set DEBUG=False
2. Configure PostgreSQL
3. Configure ALLOWED_HOSTS
4. Set environment variables
5. Run migrations
6. Run collectstatic
7. Configure web server (Gunicorn + Nginx or PaaS)

Recommended Platforms:
- Render
- Liara
- Railway
- VPS


Current Limitations
-------------------
- No shopping cart
- No authentication
- No payment system
- No email system
- Admin-only management


Future Roadmap
--------------
Phase 2:
- Shopping cart
- User authentication
- Email notifications

Phase 3:
- Online payment integration
- Discount system
- Advanced product filtering
- Admin analytics dashboard


License
-------
Internal / Client Demo Use

Project Status
--------------
Production-ready for catalog usage.
Designed for daily admin updates.
Extensible for full e-commerce in future phases.