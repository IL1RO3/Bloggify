# Bloggify

Bloggify is a self-hostable Django blog and note-taking website. It gives you a simple place to publish public posts, keep draft notes, organize writing by category, and manage content from a personal dashboard.

The project is currently in active development and will be deployed soon. Until the hosted version is available, you can run it locally or self-host it on your own server.

## Features

- Public homepage for published posts
- Post detail pages with slug-based URLs
- User registration, login, logout, and dashboard pages
- Draft workflow for private notes and unpublished writing
- Staff/admin publishing workflow for public posts
- Create, edit, and delete posts from the dashboard
- Categories for organizing blog posts and notes
- Comment form on posts
- Admin moderation for comments
- Django admin actions for publishing posts and activating comments
- PostgreSQL configuration through service and password files

## Use Cases

Bloggify can be used as:

- A personal self-hosted blog
- A private or public note-taking website
- A writing dashboard for drafts, ideas, and published articles
- A small team knowledge base or journal
- A Django learning project for authentication, CRUD views, admin customization, and PostgreSQL setup

## Tech Stack

- Python
- Django 6
- PostgreSQL
- psycopg2
- HTML templates
- CSS

## Project Structure

```text
.
|-- README.md
|-- requirements.txt
|-- manage.py
|-- .pgpass.example
|-- bloggify/
|   |-- admin.py
|   |-- forms.py
|   |-- models.py
|   |-- urls.py
|   |-- views.py
|   |-- migrations/
|   |-- static/
|   `-- templates/
`-- bloggify_project/
    |-- settings.py
    |-- urls.py
    |-- asgi.py
    `-- wsgi.py
```

## Security Notes

No real database password should be committed to this repository.

- Put your local PostgreSQL password in `.my_pgpass`
- Keep production secrets in environment variables
- Do not commit `.my_pgpass`, `.pgpass`, `.pg_service.conf`, `.env`, or `.env.*`
- Keep `.pgpass.example` as placeholders only
- Set a real `DJANGO_SECRET_KEY` before production deployment

The `.gitignore` file is configured to ignore local credential files.

## Requirements

- Python 3.12 or newer
- PostgreSQL
- pip
- virtualenv, optional but recommended

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

Create or update your PostgreSQL service file. This file usually lives outside the project at `~/.pg_service.conf`:

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

Run migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

Open the app:

```text
http://127.0.0.1:8000/blogs/
```

Open the admin panel:

```text
http://127.0.0.1:8000/admin/
```

## Configuration

The project works locally with the default development settings, but these environment variables are available for deployment:

| Variable | Purpose | Default |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key for production | Local development placeholder |
| `DJANGO_DEBUG` | Enables or disables debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed domains | Empty list |
| `POSTGRES_SERVICE` | PostgreSQL service name | `my_service` |
| `POSTGRES_PASSFILE` | PostgreSQL password file path | `.my_pgpass` |

Generate a production secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Example production environment:

```bash
export DJANGO_SECRET_KEY="replace-this-with-a-generated-secret"
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS="example.com,www.example.com"
export POSTGRES_SERVICE="my_service"
export POSTGRES_PASSFILE="/path/to/.my_pgpass"
```

## How Publishing Works

Regular users can create posts from the dashboard. These posts start as drafts, which makes Bloggify useful as a note-taking space or writing workspace.

Staff users can publish posts immediately. Admin users can also publish posts later from the Django admin using the custom bulk action.

Comments are created as inactive by default and can be approved from the Django admin before appearing publicly.

## Useful Commands

Run the development server:

```bash
python manage.py runserver
```

Create migrations after model changes:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

Run tests:

```bash
python manage.py test
```

Collect static files for deployment:

```bash
python manage.py collectstatic
```

## Self-Hosting Notes

Before using Bloggify in production:

- Set `DJANGO_SECRET_KEY`
- Set `DJANGO_DEBUG=False`
- Add your domain to `DJANGO_ALLOWED_HOSTS`
- Configure HTTPS
- Serve static files through your web server or storage provider
- Use a production WSGI or ASGI server such as Gunicorn, uWSGI, Daphne, or Uvicorn
- Keep `.my_pgpass`, `.env`, and other secret files out of Git
- Configure database backups

## Roadmap

- Public deployment
- Password reset flow
- More tests for models and views
- Production deployment documentation
- Better ownership checks for editing and deleting posts
- Rich text or Markdown editing for notes and posts

## Contributing

Contributions are welcome. For larger changes, open an issue first so the implementation can be discussed.

To contribute:

```bash
git checkout -b feature/your-feature-name
python manage.py test
```

Then open a pull request with a short explanation of the change.

## Acknowledgements

The CSS styles in `bloggify/static/bloggify/styles.css` were entirely written by Codex 5.5 Extra High.

## License

This project is licensed under the BSD 3-Clause License. See `LICENSE` for details.
