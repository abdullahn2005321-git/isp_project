# ISP Management API

A subscriber management API for an ISP service built with Flask, SQLAlchemy, JWT, and Alembic.

## Features

- Admin and staff registration and login
- Area management
- Subscriber management
- Payment processing and subscription renewal
- Daily reports and activity logs
- CORS support and ready-to-use Flask application

## Project Structure

- `app.py` - Application entry point and Flask setup
- `models.py` - Database models definition
- `routes/` - API blueprints: `auth`, `subscribers`, `payments`, `logging_and_reporting`
- `frontend/` - Static frontend files
- `migrations/` - Alembic migration history
- `requirements.txt` - Project dependencies
- `.gitignore` - Git ignore rules for environment and cache files

## Requirements

- Python 3.10 or newer
- Local virtual environment `isp/`
- MySQL or MariaDB database

## Setup

1. Activate the virtual environment:

   ```powershell
   .\isp\Scripts\activate
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following values:

   ```env
   DATABASE_URL=mysql+pymysql://root:@127.0.0.1/isp_db
   SECRET_KEY=your_secret_key_here
   ```

   > Replace the database connection and `SECRET_KEY` values with your own configuration.

4. Apply database migrations:

   ```powershell
   set FLASK_APP=app.py
   set FLASK_ENV=development
   flask db upgrade
   ```

   To create a new migration from scratch:

   ```powershell
   flask db revision --autogenerate -m "Initial migration"
   flask db upgrade
   ```

## Running the Application

```powershell
python app.py
```

Then open the browser at:

```
http://127.0.0.1:5000
```

## API Documentation

### Authentication

#### POST `/api/register`
- Description: Register a new admin user.
- Request JSON:
  - `username` (string, required)
  - `password` (string, required)
- Success response: `201`
- Error responses: `400` for missing or duplicate username, `500` for server error.

#### POST `/api/login`
- Description: Authenticate a user and receive a JWT access token.
- Request JSON:
  - `username` (string, required)
  - `password` (string, required)
- Success response: `200` with fields:
  - `token` (JWT token)
  - `role` (`admin` or `staff`)
  - `username`
- Error response: `400` for missing credentials, `401` for invalid login.

#### POST `/api/register-staff`
- Description: Create a new staff user. Requires an admin JWT token.
- Authorization: `Bearer <token>`
- Request JSON:
  - `username` (string, required)
  - `password` (string, required)
- Success response: `201`
- Error responses: `400` for missing data or duplicate username, `403` for insufficient permissions.

### Areas

#### POST `/api/areas`
- Description: Add a new service area for the current admin.
- Authorization: `Bearer <token>`
- Request JSON:
  - `name` (string, required)
- Success response: `201`
- Error responses: `400` for missing name or duplicate area, `403` for non-admin user.

#### GET `/api/areas`
- Description: List all areas owned by the current admin.
- Authorization: `Bearer <token>`
- Success response: `200` with:
  - `areas`: array of area objects `{ id, name }`

### Subscribers

#### POST `/api/subscribers`
- Description: Create a new subscriber record.
- Authorization: `Bearer <token>`
- Request JSON:
  - `name` (string, required)
  - `phone_number` (string, required)
  - `area_id` (integer, required)
  - `parent_company_id` (string, optional)
  - `balance` (number, optional)
  - `promise_date` (string date, optional)
  - `notes` (string, optional)
- Success response: `201` with `subscriber_id`.
- Error responses: `400` for missing fields or duplicate phone number.

#### GET `/api/subscribers`
- Description: Retrieve active subscribers for the current admin.
- Authorization: `Bearer <token>`
- Query parameters:
  - `page` (integer, optional, default `1`)
  - `per_page` (integer, optional, default `50`)
- Success response: `200` with subscriber list and pagination metadata.

#### GET `/api/subscribers/<id>`
- Description: Retrieve a single active subscriber by ID.
- Authorization: `Bearer <token>`
- Success response: `200` with subscriber details.
- Error response: `404` if not found.

#### PUT `/api/subscribers/<id>`
- Description: Update subscriber fields.
- Authorization: `Bearer <token>`
- Request JSON may include any of:
  - `name`
  - `phone_number`
  - `area_id`
  - `parent_company_id`
  - `notes`
  - `promise_date`
- Success response: `200`.
- Error responses: `404` if subscriber or area not found, `400` for duplicate phone.

#### DELETE `/api/subscribers/<id>`
- Description: Soft-delete a subscriber by marking `is_active` false.
- Authorization: `Bearer <token>` (admin only)
- Success response: `200`.
- Error responses: `403` for non-admin, `404` if subscriber not found.

#### GET `/api/promises_today`
- Description: List active subscribers with a payment promise date equal to today.
- Authorization: `Bearer <token>`
- Success response: `200` with subscriber list and count.

### Payments and Renewals

#### POST `/api/payments`
- Description: Record a payment and increase subscriber balance.
- Authorization: `Bearer <token>`
- Request JSON:
  - `subscriber_id` (integer, required)
  - `amount` (number, required, must be greater than `999`)
- Success response: `201` with updated balance and payment timestamp.
- Error responses: `400` for invalid amount, `404` if subscriber not found.

#### POST `/api/renewals`
- Description: Record a renewal and update debt or cash payment state.
- Authorization: `Bearer <token>`
- Request JSON:
  - `subscriber_id` (integer, required)
  - `amount` (number, required, must be greater than `999`)
  - `is_cash` (boolean, optional)
  - `promise_date` (string date, required only when balance becomes negative)
- Behavior:
  - If `is_cash` is `true`, the amount is also recorded as a payment and promise date is cleared when the balance is non-negative.
  - If `is_cash` is `false` and balance becomes negative, `promise_date` must be provided.
- Success response: `201` with updated balance.
- Error responses: `400` for invalid amount or missing promise date, `404` if subscriber not found.

### Reports and Logs

#### GET `/api/daily_report`
- Description: Get a daily summary report for payments and renewals.
- Authorization: `Bearer <token>`
- Query parameters:
  - `date` (string, optional, format `YYYY-MM-DD`, defaults to today)
- Success response: `200` with summary totals and report status.

#### GET `/api/logs`
- Description: Get the latest activity log entries for payments and renewals.
- Authorization: `Bearer <token>`
- Success response: `200` with up to 50 log records.

### Authorization Header

All protected routes require the JWT token in the request header:

```http
Authorization: Bearer <token>
```

## Notes

- Make sure the `isp_db` database exists before running the app.
- Include `migrations/` in the repository because it stores the database schema history.
- Do not include the `isp/` virtual environment folder in your GitHub repository.

