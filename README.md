# OrbitHR — Employee Management System

OrbitHR is a clean, responsive employee directory built with Flask and MySQL. It gives teams a focused workspace for viewing workforce metrics, managing employee profiles, and exploring the organization through search, filters, sorting, and pagination.

## Highlights

- Live dashboard with employee count, department count, average salary, and highest-average-salary department.
- Complete employee CRUD workflow with authenticated access, modal add/edit, offcanvas details, popover deletion, and bulk actions.
- Directory search across names, email addresses, and departments.
- Department and salary-range filters that can be combined with search.
- Sortable name, email, department, and salary columns.
- Server-side pagination with 5- or 10-row page sizes.
- Persistent query parameters while navigating pages and changing sort order.
- Responsive interface built with Bootstrap 5, Bootstrap Icons, Chart.js, and custom CSS.
- Idempotent demo-data seeding for quick local setup.
- Friendly database-unavailable screen when MySQL cannot be reached.
- Versioned database schema managed through Flask-Migrate and Alembic.

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | Python, Flask 3.1 |
| ORM | Flask-SQLAlchemy, SQLAlchemy 2 |
| Database | MySQL 8+ |
| Driver | PyMySQL |
| Migrations | Flask-Migrate, Alembic |
| Configuration | `python-dotenv` and environment variables |
| Frontend | Jinja templates, Bootstrap 5, Bootstrap Icons, custom CSS and JavaScript |

## Requirements

- Python 3.11 or newer
- MySQL 8.0 or a compatible MySQL server
- Git

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/SamarMakkar30/MyFlaskProject.git
cd MyFlaskProject
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the MySQL database

Create a database and a dedicated local user. Replace the password with a strong value of your own:

```sql
CREATE DATABASE employee_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'ems_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON employee_db.* TO 'ems_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configure environment variables

Copy the example file and update it with your local MySQL credentials:

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
FLASK_DEBUG=false
```

`.env` is ignored by Git. Never commit real passwords, secret keys, or other credentials.

### 6. Apply the database migration

```bash
flask --app app.py db upgrade
```

This creates the `employees` table from the committed Alembic migration.

### 7. Load optional demo data

```bash
python seed.py
```

The seed script adds 30 sample employees across Engineering, People Operations, Sales, Marketing, and Finance. It is safe to run repeatedly because existing email addresses are skipped.
The seed script also upgrades the legacy demo credentials to secure password hashes when an older local database is detected.

### Demo login

After running `python seed.py`, use any seeded employee account:

```text
Email: aarav.mehta@example.com
Password: demo-password
```

This is demo-only data for local evaluation. Do not use this password for a real deployment.

### 8. Run the application

```bash
python app.py
```

Open [http://127.0.0.1:5000/home](http://127.0.0.1:5000/home) in your browser.

## Application routes

| Page | Method | Route |
| --- | --- | --- |
| Dashboard | GET | `/home` |
| Employee directory | GET | `/employee/list` |
| Add employee form | GET | `/employee/register` |
| Create employee | GET, POST | `/employee/add` |
| Employee profile | GET | `/employee/employeeDetail/<id>` |
| Update employee | GET, POST | `/employee/employeeUpdate/<id>` |
| Delete employee | POST | `/employee/employeeDelete/<id>` |
| Department overview | GET | /department |
| Login / logout | GET/POST | /login, /logout |

The employee directory accepts these query parameters:

- `q` — searches name, email, and department.
- `department` — filters by an exact department.
- `min_salary` and `max_salary` — filter the salary range.
- `sort_by` — `name`, `email`, `department`, or `salary`.
- `order` — `asc` or `desc`.
- `page` — requested result page.
- `per_page` — `5` or `10` results per page.

Example:

```text
/employee/list?q=engineering&min_salary=70000&sort_by=salary&order=desc&per_page=10
```

## Project structure

```text
.
├── app.py                         # Application entry point
├── config.py                      # Environment-based Flask and database config
├── seed.py                        # Idempotent demo-data loader
├── requirements.txt               # Python dependencies
├── app/
│   ├── __init__.py                # Application factory and error handling
│   ├── models/                    # SQLAlchemy database models
│   ├── routes/                    # Dashboard, employee, and department blueprints
│   ├── static/                    # Custom CSS and JavaScript
│   └── templates/                 # Jinja page templates
├── migrations/                    # Flask-Migrate/Alembic configuration and revisions
├── .env.example                   # Safe configuration template
└── .gitignore                     # Local secrets and generated files excluded from Git
```

## Database and migrations

The application uses `employees` and `departments` tables with the following fields:

| Column | Type | Notes |
| --- | --- | --- |
| `id` | Integer | Primary key |
| `name` | String | Required, up to 100 characters |
| `email` | String | Required and unique |
| `password` | String(255) | Required, securely hashed credential |
| `salary` | Float | Required |
| `department_id` | Integer | Required foreign key to `departments` |

Create a new migration after changing models:

```bash
flask --app app.py db migrate -m "Describe the schema change"
flask --app app.py db upgrade
```

Use `db upgrade` for a fresh or existing database rather than calling `db.create_all()`, so the schema remains tracked by migrations.

## Configuration notes

`config.py` loads `.env` values while allowing host environment variables to take precedence. The database engine is configured with `pool_pre_ping` and a 280-second connection recycle interval to reduce failures from stale MySQL connections.

If MySQL is stopped or the credentials are invalid, database-backed pages return a friendly 503 page. Check that MySQL is running and verify the values in `.env` before retrying.

## Security considerations

- Passwords are hashed with Werkzeug and never rendered into forms or pages.
- All state-changing requests use POST and require a session CSRF token.
- Server-side validation rejects malformed email addresses, missing fields, non-positive salaries, and duplicate email addresses.
- Database failures return a friendly 503 page rather than a traceback.
- Set FLASK_DEBUG=false outside local development and use a strong SECRET_KEY.

## Development notes

- Run the app with `python app.py` during local development.
- Set `FLASK_DEBUG=false` outside local development.
- Keep `.env` private; commit only `.env.example`.
- The frontend loads Google Fonts, Bootstrap, and Bootstrap Icons from CDNs.
- The application currently serves the dashboard at `/home`; there is no root `/` redirect.

## License

No license has been specified yet. Add a `LICENSE` file before distributing this project publicly.





