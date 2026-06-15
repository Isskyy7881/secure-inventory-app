# Secure Inventory — IKB21503 Mini Project

A small but fully functional **secure web application** built with Django.
It demonstrates OWASP-aligned secure coding: role-based access control,
strong password hashing, CSRF protection, server-side input validation,
output encoding, secure sessions, and an audit log.

> Course: IKB21503 Secure Software Development · Group **L03_B03**
> This repository is the foundation built by **Member 1 (Core Developer)**.

---

## 1. Project description

The system is an inventory management application with two roles:

| Role | What they can do |
|------|------------------|
| **Administrator** | Full CRUD on items, view the audit log, manage own profile |
| **Normal user** | View items, manage own profile |

Core modules (each is a Django app):

- `accounts` — custom user model, registration, login, RBAC, profile
- `inventory` — the secure CRUD module (stock items)
- `auditlog` — records login attempts and key actions; admin-only viewer
- `config` — settings, URLs, custom error pages

---

## 2. Security features summary

| Area | Control implemented |
|------|---------------------|
| Input validation | Server-side form validation; SKU whitelist (regex) |
| SQL injection | Django ORM only — parameterised queries, no raw SQL |
| XSS | Template auto-escaping (output encoding on all user data) |
| CSRF | Enabled site-wide; tokens on every POST form |
| Authentication | Argon2 password hashing; strong password validators |
| Sessions | HttpOnly + SameSite cookies; 30-minute idle timeout; `Secure` flag in production |
| Access control | RBAC enforced at the view layer; no IDOR (profile = own record only) |
| Error handling | Custom 400/403/404/500 pages; no stack traces leaked |
| File upload | Avatar type + size validation; stored under a random UUID name |
| Configuration | Secrets in `.env` (never committed); `DEBUG=False` in production |
| Logging | Audit log of security events; **no passwords/tokens stored** |
| Headers | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, Referrer-Policy |

---

## 3. Requirements

- Python 3.10 or newer
- pip

All Python packages are listed in `requirements.txt`.

---

## 4. Installation steps

```bash
# 1. Go into the project folder
cd secure-inventory-app

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your environment file from the example, then edit the values
copy .env.example .env        # Windows
# cp .env.example .env        # Linux / macOS
#   -> set a new SECRET_KEY (see the comment inside the file)

# 5. Create the database tables
python manage.py migrate

# 6. (Optional) load demo accounts + sample items
python manage.py seed_demo
```

---

## 5. How to run the app

```bash
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser.

### Demo accounts (created by `seed_demo`)

| Username | Password | Role |
|----------|----------|------|
| `admin` | `Admin@12345` | Administrator |
| `staff1` | `Staff@12345` | Normal user |

> These are demo credentials for local testing only. Change them before any real use.

To create your own administrator instead:

```bash
python manage.py createsuperuser
```

---

## 6. Running the tests

The project ships with automated tests that prove the security controls work
(RBAC blocks normal users, failed logins are logged, the SKU whitelist rejects
bad input, etc.):

```bash
python manage.py test
```

Expected result: **9 tests, OK**.

---

## 7. Dependencies

See `requirements.txt`:

- `Django>=5.0,<6.0`
- `argon2-cffi` — Argon2 password hashing
- `python-dotenv` — load secrets from `.env`
- `Pillow` — image handling for avatar uploads

---

## 8. Repository structure

```
secure-inventory-app/
├── config/             # settings, urls, error handlers, wsgi/asgi
├── accounts/           # user model, RBAC, auth, profile
├── inventory/          # secure CRUD module (+ tests.py)
├── auditlog/           # audit log model, signals, admin viewer
├── templates/          # HTML templates (auto-escaped)
├── static/css/         # stylesheet
├── docs/               # report + screenshots
├── manage.py
├── requirements.txt
├── .env.example        # copy to .env (real .env is gitignored)
└── .gitignore
```

---

## 9. Screenshots

See `docs/screenshots/` for captured screens (home, login, dashboard,
inventory list, add/edit item, audit log, profile).

---

## 10. Notes for the team

- **Member 2 (Tester):** run Bandit / `pip-audit` against this code; OWASP ZAP
  against the running app. A starting point is in `docs/TEAM_HANDOFF.md`.
- **Member 3 (Mitigator):** the Manual Code Review Checklist and the place each
  control lives are listed in `docs/TEAM_HANDOFF.md`.
- **Member 4 (DevOps):** `.env.example`, `.gitignore`, `requirements.txt`, and
  this README are ready for the GitHub repository.
