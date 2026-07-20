# Kasbi Beauty — E-Commerce Project Management System

A full Django e-commerce platform for Kasbi Beauty, covering the complete customer
shopping journey (browse, search, filter, wishlist, cart, checkout, order tracking)
and an admin backpanel for managing the store (products, categories, orders,
customers, stock, discounts, and sales reports).

## Tech stack

- Python 3 / Django 6
- PostgreSQL (configured via `.env`; SQLite fallback for quick local testing)
- Bootstrap 5 (frontend)
- Pillow (image handling for product photos, logo, favicon)

## Project structure

```
kasbi/
├── kasbi/          # project settings, root urls
├── core/           # home, about, contact, site settings, contact messages
├── accounts/       # register, login, logout, profile (extends Django auth)
├── products/       # Category, Brand, Product, Wishlist, Coupon + storefront views
├── cart/           # Cart, CartItem + add/update/remove views
├── orders/         # Order, OrderItem, Payment + checkout, history, tracking
├── dashboard/      # custom admin backpanel (stats, sales report, quick actions)
├── templates/      # all HTML templates (Bootstrap 5 based)
├── static/         # css, logo.png, favicon.ico
├── media/          # uploaded product images (created at runtime)
├── db.sqlite3      # SQLite database (default, already migrated & seeded)
├── .env            # local environment config (DB engine, credentials, secret key)
└── .env.example    # template documenting every .env variable
```

## Getting started

The project ships pre-configured with **SQLite** (already migrated + seeded) so you
can run it instantly. Switch to **PostgreSQL** whenever you're ready — steps below.

### 1. Quick start (SQLite, zero setup)

```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python manage.py runserver
```

### 2. Switch to PostgreSQL

1. Create the database (adjust user/password as needed):

   ```
   psql -U postgres -c "CREATE DATABASE kasbi_beauty;"
   ```

2. Copy `.env.example` values into your `.env` (a `.env` already exists in this
   project set to SQLite — just edit it):

   ```
   DB_ENGINE=postgres
   DB_NAME=kasbi_beauty
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. Run migrations against the new database and reseed sample data:

   ```
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py seed_data
   ```

   (Your existing SQLite `db.sqlite3` data does **not** carry over automatically —
   Postgres starts empty, which is why you re-run `migrate` and `seed_data`.)

4. Run the server as usual:

   ```
   python manage.py runserver
   ```

All DB settings — engine, name, user, password, host, port, secret key, debug flag,
allowed hosts — are read from `.env` via `python-decouple`, so nothing is hardcoded
and you never commit real credentials. `.env.example` documents every variable.

### Visit the site

- Storefront: http://127.0.0.1:8000/
- Admin backpanel (custom dashboard): http://127.0.0.1:8000/dashboard/
- Full Django admin (CRUD for everything): http://127.0.0.1:8000/admin/

### Default admin login

- Username: `admin`
- Password: `Kasbi@2026`

**Change this password immediately** if you deploy this anywhere beyond your own machine.

### Sample data already loaded

6 categories, 5 brands, 12 products, and a coupon code `WELCOME10` (10% off) were
seeded automatically. To re-run the seed command later (e.g. after a fresh migrate):

```
python manage.py seed_data
```

## Feature checklist (mapped to your user stories)

**Customer**

- Register / Login / Logout — `accounts/`
- Browse, view detail, search, filter (category/brand/price), sort — `products/`
- Wishlist add/remove — `products/`
- Cart add/update/remove — `cart/`
- Checkout with coupon support, multiple payment methods — `orders/`
- Order history + status tracking — `orders/`
- Profile management — `accounts/`
- Contact support form — `core/`
- About page — `core/`

**Administrator (backpanel)**

- Secure admin login — Django auth + `/admin/`
- Dashboard with sales/orders/stock overview — `dashboard/`
- Product CRUD, category CRUD — Django admin (`products/admin.py`)
- Order management (status updates, payment tracking) — Django admin (`orders/admin.py`)
- Customer account viewing — Django admin (built-in User admin)
- Stock level updates — inline-editable in Product admin list view
- Coupons / promotions CRUD — `products/admin.py` (Coupon model)
- Sales & order reports — `/dashboard/` (top products, revenue, low stock alerts)

## Notes

- The admin backpanel CRUD uses Django's built-in admin (customized per model with
  search, filters, and inline editing) rather than hand-rolled DataTable pages —
  this gives you full, secure CRUD for every entity out of the box. If you'd like,
  I can also build a custom Bootstrap + DataTables backpanel to match your other
  projects' style — just ask.
- Product images, logo, and favicon are stored under `media/` and `static/img/`.
- For production, set `DEBUG = False`, configure `ALLOWED_HOSTS`, switch to
  PostgreSQL (matches your other projects), and set a real `SECRET_KEY` via
  environment variable.
