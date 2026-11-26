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

## Deploying on Vercel + Cloud MySQL

Vercel serverless functions cannot connect to your local XAMPP MySQL (`127.0.0.1`), so use a hosted MySQL database (e.g. **Aiven for MySQL**, **TiDB Cloud Serverless**, or **Railway MySQL**).

1. Add these **Environment Variables** in **Vercel → Project Settings → Environment Variables**:
   - `DJANGO_SECRET_KEY`: a strong random string
   - `DJANGO_DEBUG`: `False`
   - `CAREMATE_DB_NAME`: your cloud MySQL database name
   - `CAREMATE_DB_USER`: your cloud MySQL username
   - `CAREMATE_DB_PASSWORD`: your cloud MySQL password
   - `CAREMATE_DB_HOST`: your cloud MySQL host
   - `CAREMATE_DB_PORT`: your cloud MySQL port (e.g. `3306` or provider port)
   - `CAREMATE_DB_SSL`: `True` (if your cloud MySQL provider requires TLS/SSL)
2. Run migrations and seed data once from your local machine pointing at the cloud MySQL DB:
   ```powershell
   $env:CAREMATE_DB_HOST="your-cloud-host"
   $env:CAREMATE_DB_PORT="3306"
   $env:CAREMATE_DB_NAME="caremate"
   $env:CAREMATE_DB_USER="your-user"
   $env:CAREMATE_DB_PASSWORD="your-password"
   $env:CAREMATE_DB_SSL="True"
   .\.venv\Scripts\python.exe manage.py migrate
   .\.venv\Scripts\python.exe manage.py seed_caremate
   .\.venv\Scripts\python.exe manage.py createsuperuser
   ```
3. Push to GitHub (`main`) — Vercel will automatically build `caremate_project/wsgi.py` using `vercel.json` and serve static files via WhiteNoise.
