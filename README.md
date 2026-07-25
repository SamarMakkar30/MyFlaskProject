# Employee Management System

A Flask + SQLAlchemy employee directory with CRUD, server-side pagination, search, sorting, department/salary filters, and a live workforce dashboard.

## Local setup

Requirements: Python 3.11+ and MySQL 8+ (or a compatible MySQL server).

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## MySQL configuration and first run

The app uses the PyMySQL SQLAlchemy driver. Credentials live only in your local environment; never put them in `config.py` or commit a `.env` file.

1. Create a database and a least-privilege user in MySQL:

```sql
CREATE DATABASE employee_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ems_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON employee_db.* TO 'ems_user'@'localhost';
FLUSH PRIVILEGES;
```

2. Copy the example settings and enter your own local values:

```powershell
Copy-Item .env.example .env
```

```dotenv
DB_USER=ems_user
DB_PASSWORD=choose-a-strong-password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=employee_db
SECRET_KEY=replace-with-a-long-random-secret
FLASK_DEBUG=true
```

3. Apply the committed migration to the fresh database:

```powershell
flask --app app.py db upgrade
```

4. Add the idempotent demo dataset (30 employees across Engineering, People Operations, Sales, Marketing, and Finance):

```powershell
python seed.py
```

5. Start the app and open `http://127.0.0.1:5000/home`:

```powershell
python app.py
```

`flask --app app.py db upgrade` uses the same `.env` configuration as the app and seed script. The engine enables `pool_pre_ping` and a 280-second connection recycle interval so stale MySQL connections are refreshed before use.

## Database availability

If MySQL is stopped or credentials are invalid, database-backed pages return a friendly **Database unavailable** screen instead of exposing a raw SQLAlchemy/driver traceback. Start MySQL, check `.env`, and retry the page.

## Employee directory features

- Search across employee name, email, and department.
- Filter by department and salary range.
- Sort by name, email, department, or salary.
- Paginate with 5 or 10 rows per page while retaining the active filters and sort.
- Dashboard cards use SQLAlchemy aggregate queries for employee count, department count, average salary, and the highest-average-salary department.

## Routes

| Page | URL |
| --- | --- |
| Dashboard | `/home` |
| Employee list | `/employee/list` |
| Add employee | `/employee/add` |
| Employee detail | `/employee/employeeDetail/<id>` |
| Edit employee | `/employee/employeeUpdate/<id>` |
| Department overview | `/department` |

## Notes for development

- `.env.example` is safe to commit; `.env` is ignored by Git.
- `seed.py` only inserts missing demo email addresses, so it is safe to run again.
- The migration is already included under `migrations/`. Do not use `db.create_all()` for a fresh environment; use `flask --app app.py db upgrade` so the schema remains versioned.
