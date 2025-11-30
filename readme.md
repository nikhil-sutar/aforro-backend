# Aforro Backend

A production-ready, containerized E-commerce backend module built with Django and Django REST Framework. This project demonstrates high-performance API design, concurrency handling, asynchronous processing, and scalability best practices.

## Features

- Atomic Order Processing: Handles race conditions using database locks (select_for_update) and atomic transactions.
- Advanced Search: Filtering by price, category, and store availability with optimized queries.
- Fast Autocomplete: Redis-backed rate-limited suggestion API.
- Asynchronous Tasks: Order confirmation emails offloaded to Celery and Redis.
- Inventory Management: Real-time stock tracking with multi-store support.
- Fully Dockerized: Seamless setup with Django, PostgreSQL, Redis, and Celery.

## Tech Stack

- Framework: Django 5.2, Django REST Framework
- Database: PostgreSQL 15
- Caching and Broker: Redis
- Async Workers: Celery 5
- Containerization: Docker and Docker Compose

## Setup Instructions

### Prerequisites
- Docker and Docker Desktop installed.
- Git installed.

### Installation

#### Step 1: Clone the repository
```bash
git clone <your-repo-url>
cd core
```

#### Step 2: Create Environment File
Create a .env file in the root directory (same level as docker-compose.yml) with the following values:

```ini
DB_NAME=ecommerce
DB_USER=admin
DB_PASSWORD=pass1234

# Docker Service Hosts
DB_HOST=ecommerce_db
REDIS_HOST=redis

# Email Settings (For Celery)
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
```

#### Step 3: Build and Start Containers
```bash
docker-compose up --build
```

Wait until the logs show that the database and web server are ready.

#### Step 4: Initialize the Database
Open a new terminal and run:

```bash
# Apply Migrations
docker-compose exec web python manage.py migrate

# Create Superuser (Admin)
docker-compose exec web python manage.py createsuperuser

# Seed Dummy Data (10+ Categories, 1200+ Products, 25 Stores)
docker-compose exec web python manage.py seed_data
```

## Docker Usage

### Common Commands

Start all services (Django, DB, Redis, Worker):
```bash
docker-compose up
```

Start in detached mode (background):
```bash
docker-compose up -d
```

View Django logs:
```bash
docker-compose logs -f web
```

View Celery worker logs:
```bash
docker-compose logs -f celery_worker
```

Stop containers and delete database volume (reset):
```bash
docker-compose down -v
```

## Sample API Requests

### 1. Authentication

#### Register User
```
POST /api/register/
```

#### Login (Get Token)
```
POST /api/token/
```

Response: Returns access and refresh tokens.

Note: Use the access token as Bearer <token> for the Order API.

### 2. Search and Discovery

#### Autocomplete (Rate Limited)
```
GET /api/search/suggest/?q=app
```

Returns fast suggestions based on prefix matches.

#### Product Search
```
GET /api/search/products/?search=iphone&price_min=50000&store_id=1&in_stock=true
```

Parameters:
- store_id: Annotates inventory count for that specific store.
- in_stock: Boolean filter to show only available items.

### 3. Orders (Requires Auth)

#### Create Order
```
POST /orders/orders/
```

Request Body:
```json
{
    "store_id": 1,
    "items": [
        { "product_id": 101, "quantity_requested": 2 },
        { "product_id": 205, "quantity_requested": 1 }
    ]
}
```

### 4. Inventory

#### List Store Inventory
```
GET /stores/1/inventory/
```

## Engineering Notes

### Caching and Rate Limiting
- Implementation: Used Redis as the backend.
- Rate Limiting: Applied ScopedRateThrottle to the Autocomplete API (/api/search/suggest/).
- Limit: Configured to 20 requests/minute per user/IP to prevent abuse of the high-frequency search endpoint.

### Asynchronous Logic (Celery)

Use Case: Sending Order Confirmation Emails.

Workflow:
1. User places order via API.
2. If transaction succeeds, transaction.on_commit triggers a Celery task.
3. Celery worker picks up the task from Redis and sends the email in the background.

Benefit: Keeps the HTTP response time low by not making the user wait for SMTP server communication.

## Scalability Considerations

### 1. Database Optimization
- Used select_related and prefetch_related in Views to eliminate N+1 query problems.
- Added db_index=True to frequently filtered fields (Product.price, Product.title, Category.name).

### 2. Concurrency Control
- Implemented Inventory.objects.select_for_update() inside an atomic transaction during order creation.
- This prevents "Overselling" when two users try to buy the last item at the exact same millisecond.

### 3. Bulk Operations
- Used bulk_create and bulk_update for inventory adjustments and data seeding to minimize database round-trips.
