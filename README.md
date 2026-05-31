# Printverse Backend (printverse-be)

Django + DRF + PostgreSQL backend for the **Printverse** multi-vendor custom T-shirt printing platform.

## Stack
- Django 5, Django REST Framework
- PostgreSQL 16
- JWT auth (SimpleJWT) + djangorestframework-simplejwt blacklist
- django-allauth + dj-rest-auth for social providers (Google, Facebook, Instagram)
- Celery + Redis for background work (mockup rendering, push notifications)
- drf-spectacular for OpenAPI/Swagger
- django-storages + boto3 (S3) for media in production
- Razorpay (India) + Stripe (international) for payments
- Firebase Admin SDK for push notifications

## Quickstart (local)

```bash
cd printverse-be
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Start postgres + redis (or use docker compose)
docker compose up -d db redis

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Django admin: http://localhost:8000/admin/ (admin@printverse.app / admin12345)

## Full stack with Docker
```bash
docker compose up --build
```

## API surface (v1)

| Module | Base path |
| --- | --- |
| Auth & Users | `/api/v1/auth/` |
| Products & Catalog | `/api/v1/products/` |
| Design Studio | `/api/v1/designs/` |
| Cart, Coupons, Orders, Checkout | `/api/v1/orders/` |
| Payments (Razorpay/Stripe), Invoices | `/api/v1/payments/` |
| Vendor Profiles, Commission, Payouts | `/api/v1/vendors/` |
| Notifications | `/api/v1/notifications/` |

### Authentication
- `POST /auth/register/` — email/password sign-up
- `POST /auth/login/` — JWT login (`access`, `refresh`)
- `POST /auth/token/refresh/`
- `POST /auth/logout/` — blacklist refresh token
- `POST /auth/social/` — `{provider, access_token}` for Google / Facebook / Instagram (tokens obtained on mobile, verified server-side via provider APIs)
- `GET/PATCH /auth/me/`
- `GET/PATCH /auth/profile/`
- CRUD `/auth/addresses/`
- `POST /auth/social/facebook/sync-photos/` — pulls user photos via Graph API
- `POST /auth/social/instagram/sync-media/` — pulls media via Instagram Basic Display API
- `GET /auth/imported-photos/?source=instagram` — list imported photos
- `POST /auth/fcm-token/` — register FCM device token

### Products
- `GET /products/categories/`
- `GET /products/items/` — filters: `gender`, `category`, `min_price`, `max_price`, `color`, `size`, `min_rating`, `search`, `ordering`
- `GET /products/items/featured/` `trending/` `new-arrivals/` `best-sellers/`
- `GET /products/items/{id}/`
- `GET/POST /products/reviews/`
- CRUD `/products/wishlist/`

### Design Studio
- CRUD `/designs/assets/` — upload PNG/JPG/SVG (multipart)
- CRUD `/designs/` — save canvas JSON per print area
- `POST /designs/{id}/render_mockup/` — queues Celery task to produce previews

### Cart / Checkout / Orders
- `GET /orders/cart/`
- CRUD `/orders/cart-items/`
- `POST /orders/cart/apply-coupon/` `{ "code": "WELCOME10" }`
- `POST /orders/checkout/` — body: `{ shipping_address_id, accept_non_returnable: true, coupon_code? }`
- `GET /orders/` — list orders (customer/vendor/admin scoped)
- `POST /orders/{id}/update-status/` — vendor/admin only
- `POST /orders/{id}/tracking/` — `{courier, tracking_number, tracking_url}`

### Payments
- `POST /payments/razorpay/create/` `{order_id}` → returns `razorpay_order_id`, key
- `POST /payments/razorpay/verify/` `{razorpay_order_id, razorpay_payment_id, razorpay_signature}`
- `POST /payments/stripe/create/` `{order_id, currency}` → returns `client_secret`
- `POST /payments/stripe/webhook/` — gateway webhook
- `GET /payments/invoice/{order_id}/` — downloads PDF invoice

### Vendor Panel
- CRUD `/vendors/profiles/` (self-registration → pending → admin approve)
- `POST /vendors/profiles/{id}/approve/` `suspend/` (admin)
- CRUD `/vendors/commissions/` (admin)
- `GET /vendors/payouts/`

### Notifications
- `GET /notifications/`
- `POST /notifications/{id}/mark-read/`
- `POST /notifications/mark-all-read/`

## Pricing Engine
Implemented in `apps/orders/pricing.py`:

```
subtotal      = Σ (base_price + color_extra) × qty
print_total   = Σ print_cost × qty   (only when design attached)
discount      = coupon (flat or percent, capped by max_discount)
shipping      = ₹50, free above ₹999
tax           = 5% of (subtotal + print − discount + shipping)
total         = subtotal + print − discount + shipping + tax
commission    = total × commission_percent
vendor_payout = total − commission
```

Commission percent resolves from `VendorProfile.commission` → falls back to `CommissionRule(is_default=True)` → `DEFAULT_COMMISSION_PERCENT` env.

## Order lifecycle
`pending → accepted → printing → packed → shipped → out_for_delivery → delivered`
Every transition writes `OrderStatusHistory` and triggers `send_order_status_notification` (FCM + in-app).

## Tests
```bash
pytest
```

## Production checklist
- Set `DJANGO_SETTINGS_MODULE=printverse.settings.prod`
- Configure `DATABASE_URL`, `REDIS_URL`, S3 vars (`USE_S3=True`)
- Set real OAuth client IDs/secrets, Razorpay/Stripe live keys
- Provide `FCM_CREDENTIALS_JSON` (raw JSON string) for FCM
- Run behind Nginx with TLS; `gunicorn` workers tuned to CPU; Celery worker + beat services

# printverse-be
