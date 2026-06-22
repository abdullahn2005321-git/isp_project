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

## Main API Endpoints

### Authentication

- `POST /api/register` - Register a new admin
- `POST /api/register-staff` - Register a new staff user (admin token required)
- `POST /api/login` - Login and receive a JWT token

### Areas

- `POST /api/areas` - Create a new area (admin only)
- `GET /api/areas` - Get all areas

### Subscribers

- `POST /api/subscribers` - Add a new subscriber
- `GET /api/subscribers` - Get subscribers list with pagination
- `GET /api/subscribers/<id>` - Get subscriber details
- `GET /api/promises_today` - Get subscribers with promises due today

### Payments and Renewals

- `POST /api/payments` - Add a payment for a subscriber
- `POST /api/renewals` - Renew a subscription (cash or credit)

### Reports and Logs

- `GET /api/daily_report` - Daily summary report
- `GET /api/logs` - Recent payment and renewal logs

## Notes

- Make sure the `isp_db` database exists before running the app.
- Include `migrations/` in the repository because it stores the database schema history.
- Do not include the `isp/` virtual environment folder in your GitHub repository.

## GitHub Upload Tips

- Add `.gitignore`, `requirements.txt`, and `README.md` to the repository.
- Do not add `isp/`, `.env`, or any temporary/cache files.
- Keep `migrations/` tracked so the database schema can be rebuilt from migrations.

---

If you want, I can also add a `curl` example section or convert this README into a bilingual English/Arabic version.
