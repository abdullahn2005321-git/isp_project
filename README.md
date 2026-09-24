# ISP Subscriber Management API

A RESTful API for managing Internet Service Provider (ISP) subscribers, subscriptions, debts/payments, and financial reporting. Built with Flask and MySQL, with role-based multi-tenant access control so multiple admins and their staff can operate independently on the same system.

**Live deployment:** https://ispproject-production-014e.up.railway.app/ (currently used for limited, internal use — not for general public release)

## Tech Stack

- **Backend:** Python, Flask, Flask Blueprints
- **Database:** MySQL, SQLAlchemy (ORM), Flask-Migrate / Alembic
- **Auth:** JWT (Flask-JWT-Extended), password hashing via Werkzeug
- **Testing:** Pytest (30 passing tests covering auth, RBAC, subscribers, and reporting)
- **DevOps:** Docker, Docker Compose, Gunicorn, GitHub Actions CI

## Key Features

- **Role-Based Access Control:** five roles (`super_admin`, `admin`, `editor`, `commenter`, `viewer`) with per-endpoint permission checks.
- **Multi-Tenancy:** each `admin` owns their own areas, subscribers, and staff; staff accounts are scoped to their parent admin and cannot see or affect another admin's data.
- **Soft Deletion:** subscribers are deactivated (`is_active` flag) rather than hard-deleted, preserving financial history. Deletion is blocked while a subscriber still has a non-zero balance.
- **Concurrency-safe transactions:** payments and renewals lock the subscriber row (`SELECT ... FOR UPDATE`) before adjusting balances, to avoid race conditions under concurrent requests.
- **Financial reporting:** daily and monthly summaries (renewals, cash vs. electronic payments collected, transaction counts), plus a filterable/paginated activity log.
- **Daily summary aggregation job:** `tasks/daily_summary.py` computes and stores each admin's daily financial totals; intended to be run on a schedule (e.g. a daily cron job), it is not triggered automatically by the web process.

## Project Structure

```
isp_project/
├── app.py                    # Flask app factory/entrypoint, config, blueprint registration
├── models.py                 # SQLAlchemy models (User, Area, Subscriber, Transaction, DailyFinancialSummary)
├── utils.py                  # Shared helpers (safe error responses)
├── routes/
│   ├── auth.py                    # Login
│   ├── admins.py                   # Admin account management (super_admin only)
│   ├── user_management.py          # Staff account management (admin only)
│   ├── subscribers.py              # Areas & subscribers CRUD
│   ├── transactions.py             # Payments & renewals
│   └── logging_and_reporting.py    # Daily/monthly reports, activity logs
├── tasks/
│   └── daily_summary.py      # Scheduled daily financial aggregation
├── migrations/                # Alembic/Flask-Migrate migrations
├── tests/                     # Pytest suite
├── frontend/                  # Static HTML/CSS/JS admin UI, served by Flask
├── create_super_admin.py      # One-time bootstrap of the super_admin account
├── seed_data.py                # Faker-based dummy subscriber generator for local testing
├── Dockerfile / docker-compose.yml
└── requirements.txt
```

## Setup

### Option 1: Docker (recommended)

```bash
git clone https://github.com/abdullahn2005321-git/isp_project.git
cd isp_project
docker-compose up -d --build
docker-compose exec web flask db upgrade
```

The API is now available at `http://127.0.0.1:5000`.

Run the test suite inside the container:

```bash
docker-compose exec -e PYTHONPATH=/app web pytest
```

### Option 2: Local (without Docker)

```bash
# 1. Create and activate a virtual environment, then install dependencies
pip install -r requirements.txt

# 2. Create a .env file in the project root (see Environment Variables below)

# 3. Apply database migrations
flask db upgrade

# 4. Create the super_admin account (reads SUPER_ADMIN_PASSWORD from .env)
python create_super_admin.py

# 5. Run the server
python app.py
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | SQLAlchemy database URI, e.g. `mysql+pymysql://root:@127.0.0.1/isp_db`. Also accepts Railway-style `MYSQLUSER`/`MYSQLPASSWORD`/`MYSQLHOST`/`MYSQLPORT`/`MYSQLDATABASE` as a fallback. |
| `SECRET_KEY` | Yes | Signing key for JWTs. |
| `SUPER_ADMIN_PASSWORD` | Yes, for `create_super_admin.py` | Password for the bootstrap `super_admin` account (username `me`). |
| `PORT` | No (default `5000`) | Port the Flask server listens on. |
| `FLASK_DEBUG` | No (default off) | Set to `1` to enable Flask's debugger for local development only — never in production. |

## Authentication & Roles

All endpoints except `POST /api/login` and the very first `POST /api/admins` call require an `Authorization: Bearer <token>` header. Roles, from highest to lowest privilege:

- **super_admin** – can create and manage `admin` accounts.
- **admin** – owns their areas, subscribers, staff and finances; full read/write access within their own data.
- **editor** – can create/update areas and subscribers, and process payments/renewals, within their admin's data.
- **commenter** – can update subscriber details (e.g. notes) but cannot create, delete, or process transactions.
- **viewer** – read-only access.

## API Endpoints

### Auth
| Method | Path | Access |
|---|---|---|
| POST | `/api/login` | Public |

### Admins (super_admin management)
| Method | Path | Access |
|---|---|---|
| POST | `/api/admins` | Public for the first admin account; `super_admin` afterward |
| GET | `/api/admins` | `super_admin` |
| PUT | `/api/admins/<id>` | `super_admin` |

### Staff (admin's team)
| Method | Path | Access |
|---|---|---|
| POST | `/api/register-staff` | `admin` |
| GET | `/api/staff` | Any authenticated user (returns own team if admin, own manager if staff) |
| PUT | `/api/my-team/<staff_id>` | `admin` (own staff only) |
| DELETE | `/api/my-team/<staff_id>` | `admin` (own staff only) |

### Areas
| Method | Path | Access |
|---|---|---|
| POST | `/api/areas` | `admin`, `editor` |
| GET | `/api/areas` | Any authenticated user |
| PUT | `/api/areas/<id>` | `admin`, `editor` |

### Subscribers
| Method | Path | Access |
|---|---|---|
| POST | `/api/subscribers` | `admin`, `editor` |
| GET | `/api/subscribers` | Any authenticated user — paginated (`page`, `per_page`), with filters: `search`, `area_id`, `debt_only`, `balance_only`, `renewal_from`, `renewal_to` |
| GET | `/api/subscribers/<id>` | Any authenticated user |
| PUT | `/api/subscribers/<id>` | `admin`, `editor`, `commenter` |
| DELETE | `/api/subscribers/<id>` | `admin`, `editor` — soft delete; blocked if balance is non-zero |

### Payments & Renewals
| Method | Path | Access |
|---|---|---|
| POST | `/api/transactions/payment` | `admin`, `editor` |
| POST | `/api/transactions/renewal` | `admin`, `editor` |

### Reports & Logs
| Method | Path | Access |
|---|---|---|
| GET | `/api/monthly-summary` | `admin`, `editor` — optional `year`, `month` query params |
| GET | `/api/daily_payment_and_renewal_report` | Any authenticated user — optional `date` query param (`YYYY-MM-DD`) |
| GET | `/api/logs` | Any authenticated user — paginated, with filters: `subscriber_id`, `start_date`, `end_date`, `renewal`, `payment` |

## Testing

```bash
pytest
```

50 tests currently cover authentication, role-based permissions, subscriber filtering, admin/staff management, and daily summary generation.

## License

MIT — see [LICENSE](LICENSE).

## Author

Abdullah — Backend Engineer, building this project to practice designing multi-tenant backend systems with role-based access control and financial data integrity.
