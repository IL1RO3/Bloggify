# Bloggify Server Migration Checklist

Use this when moving either the public hosted instance or a self-hosted instance to a new VPS.

## Collect From Old Server

- Latest PostgreSQL custom dump from `/var/backups/bloggify/postgresql/`
- Private `/etc/bloggify/bloggify.env`
- Private `/etc/bloggify/pg_service.conf`
- Private `/etc/bloggify/pgpass`
- Media uploads from `/srv/bloggify/app/media/`, if the app uses uploads
- Current Apache site config for comparison

Do not commit the private files to GitHub.

## Prepare New Server

1. Install Ubuntu packages from `DEPLOYMENT.md`.
2. Create the `bloggify` Linux user and `/etc/bloggify` directory.
3. Clone the GitHub repository to `/srv/bloggify/app`.
4. Create `/srv/bloggify/venv` and install `requirements.txt`.
5. Create the PostgreSQL role and database.
6. Copy private env and PostgreSQL config files into `/etc/bloggify/`.
7. Restore the database dump with `pg_restore`.
8. Copy media uploads, if any.
9. Install Apache config from `deploy/apache/bloggify.conf` and edit domains.
10. Run `migrate`, `collectstatic`, and `check --deploy`.
11. Issue a fresh Let's Encrypt certificate on the new server.
12. Point DNS to the new VPS IP.
13. Test login, admin, posts, password reset, and backups.

## Restore Command Shape

```bash
sudo -u postgres pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --dbname=bloggify \
  /path/to/latest-bloggify.dump
```
