# Bloggify

Bloggify is a Django blogging and note-taking app. There can be a public hosted Bloggify instance, and the same codebase can also be self-hosted by anyone who wants to run their own copy.

The repository is intentionally generic: it must not contain the production server's secrets, database passwords, Apps Script tokens, or Apache files copied directly from a live VPS.

## What It Does

- Public homepage for published posts
- Detail pages with date and slug URLs
- User registration, login, logout, and dashboard pages
- Draft workflow for private notes and unpublished writing
- Staff/admin publishing workflow for public posts
- Create, edit, and delete posts from the dashboard
- Categories for organizing posts and notes
- Comment form with admin moderation
- Password reset support through Django email backends
- PostgreSQL configuration through service and password files

## Hosted And Self-Hosted

Bloggify supports two deployment styles:

| Mode | Meaning |
| --- | --- |
| Public hosted version | The main Bloggify site operated by the project maintainer. |
| Self-hosted version | A separate copy someone runs on their own VPS, domain, database, and email setup. |

Both use the same Django app. The difference is configuration: domains, secrets, database credentials, email gateway tokens, Apache paths, and backups belong to each server.

## Tech Stack

- Python 3.12+
- Django 6
- PostgreSQL
- psycopg2
- Apache + mod_wsgi for the documented VPS deployment
- HTML templates and CSS

## Local Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Bloggify.git
cd Bloggify
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a PostgreSQL database:

```bash
createdb bloggify
```

Create a PostgreSQL service file. Locally this usually lives at `~/.pg_service.conf`:

```ini
[my_service]
host=localhost
port=5432
dbname=bloggify
user=your_username
```

Create the local password file from the example:

```bash
cp .pgpass.example .my_pgpass
```

Edit `.my_pgpass` with your real local database credentials:

```text
localhost:5432:bloggify:your_username:your_password
```

Lock down the password file:

```bash
chmod 600 .my_pgpass
```

Run migrations and start the app:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/blogs/
http://127.0.0.1:8000/admin/
```

## Configuration

Runtime configuration is controlled by environment variables.

| Variable | Purpose | Local default |
| --- | --- | --- |
| `BLOGGIFY_ENV_FILE` | Optional path to an env file loaded by settings | `/etc/bloggify/bloggify.env` if it exists |
| `DJANGO_SECRET_KEY` | Secret key for signing data | Development placeholder |
| `DJANGO_DEBUG` | Enables debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames | Empty |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins | Empty |
| `DJANGO_USE_HTTPS` | Enables HTTPS redirects and secure cookies | `False` |
| `POSTGRES_SERVICE` | PostgreSQL service name | `my_service` |
| `POSTGRES_PASSFILE` | PostgreSQL password file path | `.my_pgpass` |
| `PGSERVICEFILE` | PostgreSQL service file path | libpq default |
| `DJANGO_EMAIL_BACKEND` | Django email backend path | Console, or Apps Script if gateway URL is set |
| `DEFAULT_FROM_EMAIL` | Default sender address | `Bloggify <no-reply@localhost>` |
| `SERVER_EMAIL` | Server/error sender address | `DEFAULT_FROM_EMAIL` |
| `BLOGGIFY_MAIL_GATEWAY_URL` | Optional Google Apps Script mail gateway URL | Empty |
| `BLOGGIFY_MAIL_GATEWAY_TOKEN` | Shared token for the mail gateway | Empty |

Use `deploy/env/bloggify.env.example` as the production template. The real `/etc/bloggify/bloggify.env` must stay private. Django loads this file automatically when it exists, which keeps Apache/mod_wsgi deployments simple.

## Password Reset Email

Local development uses Django's console email backend unless configured otherwise. Password reset emails appear in the terminal running `python manage.py runserver`.

For production, use one of these:

- A normal SMTP provider with `DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- The included Apps Script gateway backend with `BLOGGIFY_MAIL_GATEWAY_URL` and `BLOGGIFY_MAIL_GATEWAY_TOKEN`

Do not commit real email tokens or app passwords.

## Deployment

The current deployment guide is Apache + mod_wsgi + PostgreSQL on one Ubuntu VPS, with optional Google Apps Script email for password resets. See `DEPLOYMENT.md`.

Commit-safe deployment assets live in `deploy/`:

```text
deploy/
|-- apache/bloggify.conf
|-- env/bloggify.env.example
|-- scripts/bloggify-db-backup
`-- migration-checklist.md
```

These files are templates. Replace example domains, paths, and usernames for each server.

## Useful Commands

```bash
python manage.py test
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py check --deploy
```

## Security Notes

- Never commit `DJANGO_SECRET_KEY`, database passwords, Apps Script tokens, Gmail app passwords, `.pgpass`, `.pg_service.conf`, or `.env` files.
- Set `DJANGO_DEBUG=False` in production.
- Set `DJANGO_ALLOWED_HOSTS` to the exact domain names.
- Use HTTPS before real users rely on login or password reset.
- Back up PostgreSQL regularly and test that backups can be restored.
