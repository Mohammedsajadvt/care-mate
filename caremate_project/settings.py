import os
from pathlib import Path
from urllib.parse import unquote, urlparse
import certifi

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-caremate-local-dev-key-change-in-production',
)

IS_VERCEL = bool(os.environ.get('VERCEL'))

DEBUG = os.environ.get('DJANGO_DEBUG', 'False' if IS_VERCEL else 'True').lower() in (
    '1',
    'true',
    'yes',
)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        'DJANGO_ALLOWED_HOSTS',
        '127.0.0.1,localhost,.vercel.app',
    ).split(',')
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        'DJANGO_CSRF_TRUSTED_ORIGINS',
        'https://*.vercel.app',
    ).split(',')
    if o.strip()
]
if os.environ.get('VERCEL_URL'):
    vercel_origin = f"https://{os.environ['VERCEL_URL']}"
    if vercel_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(vercel_origin)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'caremate_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'caremate_project.wsgi.application'

DB_URL = (
    os.environ.get('CAREMATE_DB_URL')
    or os.environ.get('DATABASE_URL')
    or os.environ.get('MYSQL_URL')
    or ''
).strip()
RAW_DB_HOST = os.environ.get('CAREMATE_DB_HOST', '').strip()
RAW_DB_PORT = os.environ.get('CAREMATE_DB_PORT', '').strip()
if not DB_URL and RAW_DB_HOST.startswith(('mysql://', 'mysql+pymysql://')):
    DB_URL = RAW_DB_HOST
    RAW_DB_HOST = ''
elif RAW_DB_HOST and ':' in RAW_DB_HOST and not RAW_DB_HOST.startswith('['):
    host_part, _, port_part = RAW_DB_HOST.rpartition(':')
    if port_part.isdigit():
        RAW_DB_HOST = host_part
        if not RAW_DB_PORT:
            RAW_DB_PORT = port_part

PARSED_DB = urlparse(DB_URL) if DB_URL else None

DB_OPTIONS = {
    'charset': 'utf8mb4',
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
}
if os.environ.get('CAREMATE_DB_SSL', 'True' if IS_VERCEL else 'False').lower() in ('1', 'true', 'yes'):
    DB_OPTIONS['ssl'] = {'ca': certifi.where()}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': (
            os.environ.get('CAREMATE_DB_NAME', '').strip()
            or (PARSED_DB.path.lstrip('/') if PARSED_DB and PARSED_DB.path.lstrip('/') else 'caremate')
        ),
        'USER': (
            os.environ.get('CAREMATE_DB_USER', '').strip()
            or (unquote(PARSED_DB.username) if PARSED_DB and PARSED_DB.username else 'root')
        ),
        'PASSWORD': os.environ.get(
            'CAREMATE_DB_PASSWORD',
            (unquote(PARSED_DB.password) if PARSED_DB and PARSED_DB.password else ''),
        ),
        'HOST': RAW_DB_HOST or (PARSED_DB.hostname if PARSED_DB and PARSED_DB.hostname else '127.0.0.1'),
        'PORT': (
            RAW_DB_PORT
            or (str(PARSED_DB.port) if PARSED_DB and PARSED_DB.port else '3306')
        ),
        'OPTIONS': DB_OPTIONS,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
WHITENOISE_USE_FINDERS = True
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/appointments/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
