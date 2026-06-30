# Bloggify Deployment Guide

This guide describes the production setup reached during the VPS deployment work:

- Ubuntu 24.04 VPS
- Apache as the public web server
- mod_wsgi daemon mode for Django
- PostgreSQL on the same server
- Let's Encrypt HTTPS through Certbot
- Password reset email through either SMTP or the Apps Script gateway backend
- PostgreSQL backups with `pg_dump` and `pg_restore`

The examples use `example.com` and `/srv/bloggify/app`. Replace them for each server. For the public hosted Bloggify instance, use the real public domain. For self-hosters, use their own domain.

## 1. Install Packages

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y \
  apache2 libapache2-mod-wsgi-py3 \
  python3-venv python3-pip python3-dev \
  build-essential libpq-dev \
  postgresql postgresql-contrib \
  git ufw certbot python3-certbot-apache
```

Enable Apache modules:

```bash
sudo a2enmod wsgi ssl rewrite headers
sudo systemctl restart apache2
```

Firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Apache Full'
sudo ufw enable
```

Do not expose PostgreSQL port `5432` publicly.

## 2. Create Users And Paths

```bash
sudo adduser --system --group --home /srv/bloggify bloggify
sudo usermod -aG bloggify www-data
sudo install -d -m 750 -o root -g bloggify /etc/bloggify
```

Clone the app:

```bash
sudo -u bloggify -H git clone https://github.com/YOUR_USERNAME/Bloggify.git /srv/bloggify/app
sudo -u bloggify -H python3 -m venv /srv/bloggify/venv
sudo -u bloggify -H /srv/bloggify/venv/bin/pip install --upgrade pip wheel
sudo -u bloggify -H /srv/bloggify/venv/bin/pip install -r /srv/bloggify/app/requirements.txt
```

## 3. PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE ROLE bloggify LOGIN;
\password bloggify
CREATE DATABASE bloggify OWNER bloggify;
\q
```

Create `/etc/bloggify/pg_service.conf`:

```ini
[bloggify]
host=127.0.0.1
port=5432
dbname=bloggify
user=bloggify
```

Create `/etc/bloggify/pgpass`:

```text
127.0.0.1:5432:bloggify:bloggify:replace-with-the-postgres-password
```

Lock them down:

```bash
sudo chown root:bloggify /etc/bloggify/pg_service.conf /etc/bloggify/pgpass
sudo chmod 640 /etc/bloggify/pg_service.conf
sudo chmod 640 /etc/bloggify/pgpass
```

## 4. Environment File

Copy `deploy/env/bloggify.env.example` to `/etc/bloggify/bloggify.env` and fill it in. Bloggify settings load this file automatically when it exists, so Apache/mod_wsgi does not need inline secret values:

```bash
sudo cp /srv/bloggify/app/deploy/env/bloggify.env.example /etc/bloggify/bloggify.env
sudo nano /etc/bloggify/bloggify.env
sudo chown root:bloggify /etc/bloggify/bloggify.env
sudo chmod 640 /etc/bloggify/bloggify.env
```

Generate a secret key:

```bash
sudo -u bloggify -H /srv/bloggify/venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 5. Django Setup

```bash
sudo -u bloggify -H bash -c '
set -a
. /etc/bloggify/bloggify.env
set +a
cd /srv/bloggify/app
/srv/bloggify/venv/bin/python manage.py migrate
/srv/bloggify/venv/bin/python manage.py collectstatic --noinput
/srv/bloggify/venv/bin/python manage.py createsuperuser
/srv/bloggify/venv/bin/python manage.py check --deploy
'
```

## 6. Apache + mod_wsgi

Install the template:

```bash
sudo cp /srv/bloggify/app/deploy/apache/bloggify.conf /etc/apache2/sites-available/bloggify.conf
sudo nano /etc/apache2/sites-available/bloggify.conf
sudo a2dissite 000-default.conf
sudo a2ensite bloggify.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

The app should open over HTTP first:

```text
http://example.com/blogs/
```

Then add HTTPS:

```bash
sudo certbot --apache -d example.com -d www.example.com
```

Set HTTPS on in `/etc/bloggify/bloggify.env`:

```bash
DJANGO_USE_HTTPS=True
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
```

Restart Apache:

```bash
sudo apache2ctl configtest
sudo systemctl restart apache2
```

## 7. Email

For local development, the console backend is enough. For production password reset emails, configure one backend.

Apps Script gateway:

```bash
BLOGGIFY_MAIL_GATEWAY_URL='https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec'
BLOGGIFY_MAIL_GATEWAY_TOKEN='replace-with-a-random-token'
DEFAULT_FROM_EMAIL='Bloggify <you@example.com>'
SERVER_EMAIL='Bloggify <you@example.com>'
```

SMTP provider:

```bash
DJANGO_EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
DJANGO_EMAIL_HOST='smtp.example.com'
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_HOST_USER='smtp-user'
DJANGO_EMAIL_HOST_PASSWORD='smtp-password'
DJANGO_EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL='Bloggify <noreply@example.com>'
SERVER_EMAIL='Bloggify <errors@example.com>'
```

The Apps Script token, SMTP password, and Django secret key are secrets. Keep them out of GitHub and chat logs.

## 8. Backups

Install the backup script:

```bash
sudo cp /srv/bloggify/app/deploy/scripts/bloggify-db-backup /usr/local/sbin/bloggify-db-backup
sudo chown root:postgres /usr/local/sbin/bloggify-db-backup
sudo chmod 750 /usr/local/sbin/bloggify-db-backup
sudo install -d -m 700 -o postgres -g postgres /var/backups/bloggify/postgresql
```

Run and verify manually:

```bash
sudo -u postgres /usr/local/sbin/bloggify-db-backup
sudo ls -lh /var/backups/bloggify/postgresql
sudo -u postgres pg_restore --list /var/backups/bloggify/postgresql/bloggify-auto-*.dump | head -20
```

If your shell cannot expand `*.dump` because of permissions, use the exact filename printed by `ls`.

A systemd timer can be added later to run this nightly.

## 9. Updating The App

```bash
sudo -u bloggify -H bash -c '
set -a
. /etc/bloggify/bloggify.env
set +a
cd /srv/bloggify/app
git pull
/srv/bloggify/venv/bin/pip install -r requirements.txt
/srv/bloggify/venv/bin/python manage.py migrate
/srv/bloggify/venv/bin/python manage.py collectstatic --noinput
'

sudo apache2ctl configtest
sudo systemctl reload apache2
```

## 10. Moving Servers Later

A future server move needs:

- GitHub code
- Latest PostgreSQL `.dump` backup
- Private `/etc/bloggify/bloggify.env`
- Private PostgreSQL service/pass files
- Apache config based on `deploy/apache/bloggify.conf`
- Media uploads, if any
- A fresh Let's Encrypt certificate on the new server

Use `deploy/migration-checklist.md` when moving.
