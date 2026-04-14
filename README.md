# Hair Palace

> Premium hair & beauty e-commerce platform — order-first marketplace for South African customers.

**Live:** [https://hairpalace.co.za](https://hairpalace.co.za)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Services](#services)
4. [Tech Stack](#tech-stack)
5. [Domain Model](#domain-model)
6. [API Reference](#api-reference)
7. [Event System](#event-system)
8. [Frontend Pages & Components](#frontend-pages--components)
9. [Email Notifications](#email-notifications)
10. [User Stories](#user-stories)
11. [Admin Stories](#admin-stories)
12. [Secrets & Environment](#secrets--environment)
13. [Local Development](#local-development)
14. [Deployment](#deployment)
15. [Testing](#testing)

---

## Project Overview

Hair Palace is a full-stack e-commerce platform specialising in hair extensions, wigs, braiding hair, hair care products, styling tools, and accessories for the South African market.

The platform uses an **order-first fulfilment model** — products can be listed with `lead_time_days > 0` meaning the business sources stock after an order is placed and paid, rather than holding large inventory upfront. This reduces capital risk while still offering a wide product catalogue.

---

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │         hairpalace.co.za (HTTPS)        │
                    └──────────────────┬──────────────────────┘
                                       │
                             ┌─────────▼─────────┐
                             │  System Nginx      │  (host, port 443)
                             │  SSL termination   │  Let's Encrypt cert
                             └─────────┬─────────┘
                                       │ proxy → localhost:3001
                    ┌──────────────────▼──────────────────────┐
                    │         Docker Compose Stack             │
                    │                                         │
                    │  ┌──────────┐    ┌──────────────────┐  │
                    │  │  Nginx   │───▶│  Next.js 15      │  │
                    │  │ (proxy)  │    │  Frontend :3000   │  │
                    │  │  :3001   │    └──────────────────┘  │
                    │  │          │    ┌──────────────────┐  │
                    │  │          │───▶│  FastAPI          │  │
                    │  └──────────┘    │  Backend :8000    │  │
                    │                  └────────┬─────────┘  │
                    │      ┌─────────────────────┤           │
                    │      │            ┌────────▼──────┐    │
                    │      │            │  PostgreSQL 16 │    │
                    │      │            │  (operational) │    │
                    │      │            └───────────────┘    │
                    │      │            ┌───────────────┐    │
                    │      │            │  Redis 7       │    │
                    │      │            └───────────────┘    │
                    │      │                                  │
                    │      │  Kafka events (hp.*)             │
                    │      ▼                                  │
                    │  ┌──────────┐    ┌──────────────────┐  │
                    │  │ Redpanda │───▶│  Analytics       │  │
                    │  │ (Kafka)  │    │  Consumer        │  │
                    │  └──────────┘    └────────┬─────────┘  │
                    │                           │            │
                    │                  ┌────────▼──────┐    │
                    │                  │  PostgreSQL 16 │    │
                    │                  │  (analytics)  │    │
                    │                  └───────────────┘    │
                    └─────────────────────────────────────────┘
```

**Key design decisions:**

- **Vertical slices** — each feature (`users`, `products`, `orders`, `admin`, `contact`) owns its own router, service, repository, schemas, and models.
- **Event-driven analytics** — domain events are published to Redpanda (Kafka-compatible) and consumed by a separate analytics service; the operational DB is never queried for analytics.
- **Order-first fulfilment** — products carry a `lead_time_days` field; `0` means in-stock, `>0` means sourced-on-demand after payment.
- **SSL at the host** — the system nginx terminates TLS; the Docker nginx handles internal routing only, bound to `localhost:3001`.

---

## Services

| Service | Image / Build | Port | Description |
|---|---|---|---|
| `nginx` | `./nginx` | `127.0.0.1:3001:80` | Internal reverse proxy — routes `/api/` to backend, everything else to frontend |
| `backend` | `./services/backend` | `8000` (internal) | FastAPI REST API with async SQLAlchemy and Alembic migrations |
| `frontend` | `./services/frontend` | `3000` (internal) | Next.js 15 storefront (App Router) with Stripe payment UI |
| `analytics` | `./services/analytics` | — | Python Kafka consumer — writes event-sourced analytics tables |
| `postgres` | `postgres:16-alpine` | `5432` (internal) | Operational database — users, products, orders |
| `analytics_db` | `postgres:16-alpine` | `5432` (internal) | Separate analytics database — event log, snapshots, lifecycles |
| `redis` | `redis:7-alpine` | `6379` (internal) | Cache and session store |
| `redpanda` | `redpandadata/redpanda:v24.2.18` | `9092` (internal) | Kafka-compatible message broker |

---

## Tech Stack

### Backend
- **Python 3.12** + **FastAPI 0.115** — async REST API
- **SQLAlchemy 2.0** (async) + **Alembic** — ORM and DB migrations
- **asyncpg** — native async PostgreSQL driver
- **Pydantic v2** / **pydantic-settings** — schema validation and config
- **python-jose** — JWT access and refresh tokens
- **bcrypt** / **passlib** — password hashing
- **stripe** — payment intent creation and webhook verification
- **httpx** — async HTTP client for Yoco / PayJustNow / Payflex / HappyPay checkout APIs
- **aiokafka** — async Kafka producer
- **smtplib** — transactional email (STARTTLS / SSL)

### Frontend
- **Next.js 15** (App Router) + **React 19** + **TypeScript**
- **Tailwind CSS** — utility-first styling
- **Zustand** — client-side state (cart, auth)
- **@stripe/react-stripe-js** — Stripe Elements checkout UI
- **framer-motion** — page/component animations
- **axios** — API client
- **react-hot-toast** — toast notifications
- **lucide-react** — icon set

### Infrastructure
- **Docker** + **Docker Compose** — containerised stack
- **Redpanda** (Kafka-compatible) — event streaming
- **Let's Encrypt** — TLS certificates (auto-renewed via certbot)
- **cPanel SMTP** (`mail.hairpalace.co.za`, port 587 STARTTLS) — outbound email

---

## Domain Model

### Users

| Field | Type | Notes |
|---|---|---|
| `id` | int PK | |
| `email` | string (unique) | Login credential |
| `hashed_password` | string | bcrypt hash |
| `full_name` | string | |
| `phone` | string (optional) | |
| `is_active` | bool | Soft-disable account |
| `is_admin` | bool | Grants admin API access |
| `created_at` | timestamptz | Server-generated |

### Products

| Field | Type | Notes |
|---|---|---|
| `id` | int PK | |
| `name` | string | |
| `slug` | string (unique) | URL-safe identifier |
| `description` | text | |
| `category` | enum | `hair_extensions`, `wigs`, `braiding_hair`, `hair_care`, `styling_tools`, `accessories` |
| `price` | decimal(10,2) | ZAR |
| `is_active` | bool | Soft-delete / hide from shop |
| `is_featured` | bool | Show on homepage |
| `lead_time_days` | int | `0` = in stock; `>0` = sourced after order |
| `stock_quantity` | int | Current available stock |

Each product has zero or more **ProductImages** (`url`, `alt_text`, `is_primary`).

### Orders

| Field | Type | Notes |
|---|---|---|
| `reference` | string (unique) | Human-readable e.g. `HP-2026-00042` |
| `status` | enum | See lifecycle below |
| `payment_provider` | enum | `stripe`, `yoco`, `payjustnow`, `payflex`, `happypay` |
| `stripe_payment_intent_id` | string | Stripe webhook confirmation |
| `external_payment_id` | string | Checkout ID from Yoco / PayJustNow / Payflex / HappyPay |
| `subtotal`, `shipping_fee`, `total` | decimal | Calculated at creation |
| `shipping_*` | strings | Denormalised address snapshot |
| `tracking_number` | string | Set by admin on shipment |
| `admin_notes` | text | Internal sourcing notes |

**Order status lifecycle:**
```
PENDING_PAYMENT → PAID → SOURCING → PROCESSING → SHIPPED → DELIVERED
                                                          ↳ CANCELLED
                                                          ↳ REFUNDED
```

Each order contains one or more **OrderItems** which snapshot `unit_price` and `product_name` at the time of order (immutable after creation).

---

## API Reference

All endpoints are prefixed with `/api/v1`. API docs are available at `/api/docs` in non-production environments.

### Auth & Users — `/api/v1/auth`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/register` | Public | Create account; triggers welcome email |
| `POST` | `/login` | Public | Email + password → access + refresh tokens |
| `POST` | `/refresh` | Public | Exchange refresh token for new access token |
| `GET` | `/me` | Customer | Get own profile |
| `PATCH` | `/me` | Customer | Update name, phone |
| `POST` | `/password-reset/request` | Public | Send reset email (silent on unknown email) |
| `POST` | `/password-reset/confirm` | Public | Verify token + set new password |

### Products — `/api/v1/products`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `` | Public | Paginated product list; filter by `category`, `featured` |
| `GET` | `/{slug}` | Public | Product detail by slug |
| `POST` | `` | Admin | Create product |
| `PATCH` | `/{product_id}` | Admin | Update product fields |
| `PATCH` | `/{product_id}/stock` | Admin | Adjust stock quantity with reason |
| `DELETE` | `/{product_id}` | Admin | Soft-delete (sets `is_active = false`) |

### Orders — `/api/v1/orders`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `` | Customer | Create order + initiate payment (provider set by `payment_provider` field) |
| `GET` | `/me` | Customer | Paginated list of own orders |
| `GET` | `/me/{order_id}` | Customer | Order detail |
| `POST` | `/webhook/stripe` | Stripe | Confirm payment on `payment_intent.succeeded` |
| `POST` | `/webhook/yoco` | Yoco | Confirm payment on `payment.succeeded` |
| `POST` | `/webhook/payjustnow` | PayJustNow | Confirm payment on `approved` IPN |
| `POST` | `/payment/payflex/confirm` | Payflex | Confirm payment after redirect callback |
| `POST` | `/webhook/happypay` | HappyPay | Confirm payment on `PAID` webhook |
| `GET` | `/admin` | Admin | All orders; filter by status |
| `PATCH` | `/admin/{order_id}` | Admin | Update status, tracking number, notes |

### Admin Dashboard — `/api/v1/admin`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/products` | Admin | All products including inactive (up to 200/page) |
| `GET` | `/orders` | Admin | All orders with optional status filter |
| `PATCH` | `/orders/{order_id}` | Admin | Status / tracking / notes update |
| `GET` | `/stats` | Admin | Revenue, order counts, top products |

### Contact — `/api/v1/contact`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `` | Public | Submit contact form — alerts admin + sends auto-reply |

---

## Event System

The backend publishes domain events to Redpanda (Kafka) on four topics. The analytics consumer subscribes to all topics and processes events idempotently (safe to replay).

### Topics

| Topic | Events |
|---|---|
| `hp.products` | `product.created`, `product.updated`, `product.price_changed`, `product.stock_adjusted`, `product.deactivated` |
| `hp.orders` | `order.created`, `order.paid`, `order.status_changed`, `order.cancelled` |
| `hp.inventory` | `inventory.adjusted` |
| `hp.users` | `user.registered` |

### Event Envelope

Every event shares the same envelope schema:

```json
{
  "event_id": "uuid-v4",
  "event_type": "product.created",
  "event_version": 1,
  "entity_type": "product",
  "entity_id": 42,
  "actor_id": 1,
  "actor_type": "admin",
  "source_service": "hairpalace-backend",
  "produced_at": "2026-04-14T07:00:00Z",
  "payload": { "...": "domain-specific data" }
}
```

### Analytics Tables

| Table | What it stores |
|---|---|
| `event_log` | Every event, idempotent on `event_id` |
| `product_snapshots` | Point-in-time product state on every change (full price/stock history) |
| `order_lifecycle` | Every order status transition (funnel / SLA analytics) |
| `inventory_movements` | Delta-log of every stock adjustment (reconciliation / shrinkage) |

Analytics tables store no PII — user events record entity IDs only, never names or emails.

---

## Frontend Pages & Components

### Pages (`/src/app/(shop)/`)

| Route | Description |
|---|---|
| `/` | Homepage — hero, featured products, how-it-works section |
| `/products` | Browse all products with category filter |
| `/products/[slug]` | Product detail with add-to-cart |
| `/checkout` | Stripe Elements payment form with shipping address |
| `/orders` | Customer order history |
| `/orders/[id]` | Order detail and status tracking |
| `/login` | Email + password login |
| `/register` | New account registration |
| `/admin` | Admin dashboard (products, orders, stats) |
| `/shipping` | Shipping policy page |
| `/returns` | Returns & refunds policy page |
| `/privacy` | Privacy policy page |
| `/terms` | Terms of service page |

### Shared Components

| Component | Description |
|---|---|
| `Header` | Site navigation, cart icon with item count, auth links |
| `Footer` | Brand info, policy links, social links |
| `HeroSection` | Homepage hero with headline and CTA |
| `ProductCard` | Reusable product tile (image, name, price, add-to-cart) |
| `CartDrawer` | Slide-in cart sidebar managed by Zustand store |
| `HowItWorks` | Explainer section — 3-step order-first process |

---

## Email Notifications

All emails are sent from `noreply@hairpalace.co.za` via `mail.hairpalace.co.za` (port 587, STARTTLS). In development (no `SMTP_HOST` set), emails are logged to stdout instead of being sent.

| Trigger | Recipient | Description |
|---|---|---|
| User registers | Customer | Welcome email with brand intro |
| Order created | Customer | Order confirmation with itemised summary |
| Password reset requested | Customer | Reset link (valid 30 minutes) |
| Contact form submitted | `info@hairpalace.co.za` | Alert with customer message and contact details |
| Contact form submitted | Customer | Auto-reply acknowledging receipt |

---

## User Stories

### Browsing & Discovery
- As a visitor, I can browse the full product catalogue and filter by category.
- As a visitor, I can see featured products highlighted on the homepage.
- As a visitor, I can view full product detail — images, description, price, and expected lead time — before deciding to buy.

### Account Management
- As a new customer, I can create an account with my name, email, and password.
- As a customer, I receive a welcome email immediately after registering.
- As a customer, I can log in and out securely.
- As a customer, I can update my name and phone number on my profile.
- As a customer, I can request a password reset link and set a new password.

### Checkout & Payment
- As a customer, I can add products to my cart and review quantities before checkout.
- As a customer, I can enter a shipping address (name, address, city, province, postal code) at checkout.
- As a customer, I can choose my preferred payment method at checkout — **Yoco** (card/EFT), **PayJustNow** (3× interest-free), **Payflex** (4× over 6 weeks), **HappyPay** (instalments), or **Stripe** (credit/debit card).
- As a customer, I am redirected to the chosen provider's hosted payment page to complete the transaction securely.
- As a customer, I receive an order confirmation email immediately after payment.
- As a customer, I can see the estimated lead time on products so I know when to expect delivery.

### Order Tracking
- As a customer, I can view all my past orders with their current status.
- As a customer, I can see full order detail — items purchased, amounts, and shipping info.
- As a customer, I can see my tracking number once my order has been dispatched.

### Contact
- As a visitor, I can submit a contact form with my name, email, and message.
- As a visitor, I receive an auto-reply confirming my message was received.

---

## Admin Stories

### Product Management
- As an admin, I can create new products with name, category, price, description, lead time, and images.
- As an admin, I can edit any product's details at any time.
- As an admin, I can adjust stock quantity with a recorded reason (e.g. "received supplier shipment").
- As an admin, I can soft-delete a product to hide it from the shop without losing its data or order history.
- As an admin, I can list all products including inactive ones to review the full catalogue.
- As an admin, I can mark products as featured so they appear on the homepage.

### Order Fulfilment
- As an admin, I can view all orders and filter by status to manage my fulfilment queue.
- As an admin, I can progress an order through the lifecycle: `PAID` → `SOURCING` → `PROCESSING` → `SHIPPED` → `DELIVERED`.
- As an admin, I can enter a courier tracking number when I dispatch an order.
- As an admin, I can add internal notes to an order to record sourcing details or supplier reference numbers.
- As an admin, I can mark an order as `CANCELLED` or `REFUNDED` when necessary.

### Dashboard & Analytics
- As an admin, I can view a stats dashboard with total revenue, order counts by status, and top-selling products.
- As an admin, full product and order history is captured as immutable Kafka events for future analytics and reporting.

### Communications
- As an admin, I receive an email alert whenever a customer submits a contact form.

---

## Secrets & Environment

Secrets use a three-file pattern to keep credentials out of version control:

| File | Purpose | Committed |
|---|---|---|
| `.hairpalace` | All real secrets as `export KEY="value"` | No (gitignored) |
| `.env` | Pure `${VAR}` placeholder template | **Yes** |
| `.env.live` | Resolved output — Docker Compose reads this | No (gitignored) |

Generate `.env.live`:
```bash
source .hairpalace && envsubst < .env > .env.live
```

### Variables in `.hairpalace`

```bash
# Server SSH
export SSH_HOST="156.155.250.65"
export SSH_USER="root"
export SSH_KEY="$HOME/.ssh/your_key"
export REMOTE_DIR="/root/hairpalace"

# App
export APP_ENV="production"
export SECRET_KEY="<64-char random>"        # openssl rand -hex 32
export JWT_SECRET="<64-char random>"        # openssl rand -hex 32

# Databases
export POSTGRES_PASSWORD="<strong password>"
export ANALYTICS_DB_PASSWORD="<strong password>"

# Stripe
export STRIPE_SECRET_KEY="sk_live_..."
export STRIPE_PUBLISHABLE_KEY="pk_live_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# Yoco
export YOCO_SECRET_KEY="sk_live_..."
export YOCO_WEBHOOK_SECRET="..."

# PayJustNow
export PJN_API_KEY="..."
export PJN_WEBHOOK_SECRET="..."

# Payflex
export PAYFLEX_SECRET="..."
export PAYFLEX_WEBHOOK_SECRET="..."

# HappyPay
export HAPPYPAY_API_KEY="..."
export HAPPYPAY_WEBHOOK_SECRET="..."

# Email (cPanel SMTP)
export SMTP_HOST="mail.hairpalace.co.za"
export SMTP_PORT="587"
export SMTP_USE_SSL="False"
export SMTP_USER="noreply@hairpalace.co.za"
export SMTP_PASSWORD="..."
export ADMIN_EMAIL="info@hairpalace.co.za"
```

---

## Local Development

### Prerequisites
- Docker Desktop
- `gettext` for `envsubst` — `brew install gettext` on macOS

### Start the stack

```bash
# 1. Create a local secrets file for dev credentials
cp .env .env.local
# Edit .env.local — replace ${VAR} placeholders with local dev values

# 2. Generate .env.live
source .env.local && envsubst < .env > .env.live

# 3. Start all 8 services
docker compose up -d --build

# 4. Run database migrations
docker exec hairpalace-backend-1 alembic upgrade head

# 5. Visit
#    Frontend: http://localhost:3001
#    API docs: http://localhost:3001/api/docs
```

---

## Deployment

The deploy script handles everything in one command:

```bash
bash scripts/deploy.sh
```

**What it does:**
1. Sources `.hairpalace` locally to load credentials
2. `scp`s `.hairpalace` to the server
3. Runs `git pull origin main` on the server
4. Runs `--local` mode on the server:
   - Resolves secrets: `envsubst < .env > .env.live`
   - Rebuilds and restarts all containers: `docker compose up -d --build --force-recreate`

### TLS / Let's Encrypt

The SSL certificate for `hairpalace.co.za` and `www.hairpalace.co.za` is managed by certbot on the host (outside Docker). It auto-renews. The system nginx proxies HTTPS → `localhost:3001` where the Docker nginx stack listens.

---

## Testing

Tests use `pytest-asyncio` with `httpx.AsyncClient` against a live PostgreSQL instance — no mocking of the database layer.

```
services/backend/tests/
├── conftest.py        # event loop, async session, test client, factories
├── test_users.py      # registration, login, refresh, profile, password reset
├── test_products.py   # CRUD, stock adjustment, category filtering, slug lookup
├── test_orders.py     # create, list, detail, Stripe webhook, admin operations
├── test_admin.py      # admin-only endpoints, stats dashboard
└── test_events.py     # Kafka event emission verification
```

Run tests in Docker (matches CI environment):

```bash
docker run --rm \
  --network hairpalace_strands_net \
  -v $(pwd)/services/backend:/app \
  -e SECRET_KEY=test-secret \
  -e DATABASE_URL=postgresql+asyncpg://strands:strands_local_dev@postgres:5432/strands \
  -e TEST_DATABASE_URL=postgresql+asyncpg://strands:strands_local_dev@postgres:5432/strands \
  -e JWT_SECRET=test-jwt-secret \
  -e STRIPE_SECRET_KEY=sk_test_dummy \
  -e STRIPE_PUBLISHABLE_KEY=pk_test_dummy \
  -e STRIPE_WEBHOOK_SECRET=whsec_dummy \
  hairpalace-backend \
  pytest --tb=short -q
```

**65 tests — 100% pass rate.**
