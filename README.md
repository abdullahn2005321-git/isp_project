# 🚀 ISP Subscriber Management API

A robust, high-performance RESTful API built to manage Internet Service Provider (ISP) subscribers, financial records (debts/payments), and automated daily reporting. Built with Python, Flask, SQLAlchemy, and MySQL, and fully containerized using Docker.

## 🔥 Technical Engineering & Skills Highlighted

As a Backend Developer, I built this project to demonstrate my ability to architect scalable business solutions using industry best practices:

- **Clean Architecture:** Code is modularized using **Flask Blueprints** (`auth`, `subscribers`, `payments`, `reports`), ensuring scalability and easy maintenance.
- **Advanced Database Design:** - Migrated from SQLite to **MySQL** for production readiness.
  - Implemented **Soft Deletion** (`is_active` flag) to prevent the accidental loss of critical financial records.
  - Used precise data types (e.g., `Integer` for currency) to prevent floating-point calculation errors.
- **Multi-Tenancy & Security:** Implemented Role-Based Access Control (RBAC) using **JWT tokens**. The system isolates data so that branch managers/staff can only access their specific subscribers.
- **DevOps & Containerization:** The entire application and database are containerized using **Docker** and **Docker Compose**, utilizing `volumes` for hot-reloading during development.
- **Performance & Load Testing:** The database schema and SQLAlchemy queries (using `joinedload` to prevent N+1 query issues) were optimized and successfully stress-tested with **100,000+ mock subscribers** generated via a custom `Faker` script, ensuring fast data retrieval and stable memory usage.
- **Automated Testing:** Integration testing implemented using **Pytest** to ensure API endpoints reliability and prevent regressions.

## 🛠️ Tech Stack
- **Backend:** Python 3.12, Flask, Flask-RESTful
- **Database:** MySQL 8.0, SQLAlchemy (ORM), Alembic (Flask-Migrate)
- **Security:** JWT (JSON Web Tokens), Flask-Bcrypt (Password Hashing)
- **DevOps:** Docker, Docker Compose
- **Testing:** Pytest

---

## 🐳 Quick Setup (Docker - Recommended)

The easiest way to run this project is using Docker. No local Python installation is required!

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/abdullahn2005321-git/isp_project.git](https://github.com/abdullahn2005321-git/isp_project.git)
   cd isp_project
Build and spin up the containers:

Bash
docker-compose up -d --build
Apply Database Migrations:

Bash
docker-compose exec web flask db upgrade
Run Automated Tests (Optional):

Bash
docker-compose exec -e PYTHONPATH=/app web pytest
The API is now live at: http://127.0.0.1:5000

💻 Local Setup (Without Docker)
If you prefer to run it locally using a virtual environment:

Activate the virtual environment:

PowerShell
.\isp\Scripts\activate
Install dependencies:

PowerShell
pip install -r requirements.txt
Configure Environment Variables:
Create a .env file in the root directory:

Code snippet
DATABASE_URL=mysql+pymysql://root:@127.0.0.1/isp_db
SECRET_KEY=your_secure_secret_key
Run migrations and start the server:

PowerShell
flask db upgrade
python app.py
📚 API Endpoints Documentation
Note: All endpoints except /login and /register require an Authorization: Bearer <token> header.

🔐 Authentication
POST /api/register - Register a new admin user.

POST /api/login - Authenticate and receive a JWT access token.

POST /api/register-staff - Create a new staff user under the current admin.

🌍 Areas
POST /api/areas - Add a new service area.

GET /api/areas - List all areas owned by the current admin.

👥 Subscribers
POST /api/subscribers - Create a new subscriber record.

GET /api/subscribers - Retrieve active subscribers (Supports Pagination).

GET /api/subscribers/<id> - Retrieve a single active subscriber.

PUT /api/subscribers/<id> - Update subscriber details.

DELETE /api/subscribers/<id> - Soft-delete a subscriber.

GET /api/promises_today - List subscribers with a payment promise date equal to today.

💰 Payments and Renewals
POST /api/payments - Record a payment and reduce subscriber debt.

POST /api/renewals - Record a monthly renewal (handles cash or debt logic dynamically).

📊 Reports and Logs
GET /api/daily_report - Get a daily financial summary of net totals and statuses. Supports historical checks via ?date=YYYY-MM-DD.

GET /api/logs - Fetch the latest 50 activity log entries.

👨‍💻 Author
Abdullah - Backend Engineer
Passionate about building scalable backend systems, clean architecture, and solving complex business problems.