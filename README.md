# CareMate — Django Appointment Booking App

CareMate is a Django + MySQL healthcare appointment booking web application with a custom CareMate-themed Django Admin panel.

## Local Development (XAMPP MySQL)

1. Start **MySQL** in XAMPP and create the database:
   ```sql
   CREATE DATABASE IF NOT EXISTS caremate CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Create a virtual environment and install dependencies:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
3. Run migrations and seed sample doctors, blog posts, and reviews:
   ```powershell
   .\.venv\Scripts\python.exe manage.py migrate
   .\.venv\Scripts\python.exe manage.py seed_caremate
   .\.venv\Scripts\python.exe manage.py createsuperuser
   ```
4. Start the development server:
   ```powershell
   .\.venv\Scripts\python.exe manage.py runserver
   ```

## Production Hosting Environment Variables

Set these environment variables on your hosting provider (PythonAnywhere, Railway, Render, or VPS):

- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY=<your-strong-random-secret>`
- `DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`
- `CAREMATE_DB_NAME=caremate`
- `CAREMATE_DB_USER=<db-user>`
- `CAREMATE_DB_PASSWORD=<db-password>`
- `CAREMATE_DB_HOST=<db-host>`
- `CAREMATE_DB_PORT=3306`

During deployment, run:
```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_caremate
```
