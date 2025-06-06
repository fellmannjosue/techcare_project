import os
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------
# Cargar variables de entorno desde .env
# -----------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# -----------------------------------
# Configuración básica
# -----------------------------------
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-n=bzqfb1q&i3jd_*l=k#0khjv98zqg!61zr1#9pdevq#5h+rp!')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.10.6',]

# -----------------------------------
# Aplicaciones instaladas
# -----------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'enfermeria',
]

# -----------------------------------
# Middleware
# -----------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_test.urls'

# -----------------------------------
# Templates
# -----------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Carpeta global de plantillas (si la usas)
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_test.wsgi.application'

# -----------------------------------
# Bases de datos
# -----------------------------------
DATABASES = {
    # Base de datos principal (MySQL Workbench → sponsors3)
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'sponsors3'),
        'USER': os.getenv('DB_USER', 'admin3'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'Test-12345'),
        'HOST': os.getenv('DB_HOST', '192.168.10.6'),
        'PORT': os.getenv('DB_PORT', '3306'),
    },

    # Conexión al SQL Server remoto (Test2)
    'padres_sqlserver': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('MSSQL_DB_NAME', 'Test2'),
        'USER': os.getenv('MSSQL_DB_USER', 'admin2'),
        'PASSWORD': os.getenv('MSSQL_DB_PASSWORD', '121800-Jfellmann'),
        'HOST': os.getenv('MSSQL_DB_HOST', '192.168.10.2'),
        'PORT': os.getenv('MSSQL_DB_PORT', '1433'),
        'OPTIONS': {
            'driver': os.getenv('MSSQL_ODBC_DRIVER', 'ODBC Driver 17 for SQL Server'),
        },
    },
}

# -----------------------------------
# Configuración de correo (SMTP)
# -----------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'techcare.app2024@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'dvex nxbf quaj nxtc')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'techcare.app2024@gmail.com')

# -----------------------------------
# Internacionalización y estáticos
# -----------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'
