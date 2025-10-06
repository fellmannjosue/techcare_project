# ─────────────────────────────────────────────────────────────
# 1. IMPORTACIONES BÁSICAS
# ─────────────────────────────────────────────────────────────
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar las variables desde el archivo .env
load_dotenv()

# ─────────────────────────────────────────────────────────────
# 2. DIRECTORIO BASE DEL PROYECTO
# ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────────────────────
# 3. SEGURIDAD
# ─────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-b(q9vw0wc#j2@pxe-kl4+(nbi0p4lth&t&nc7vy2a-*m01v!fq')
DEBUG = (os.getenv('DJANGO_DEBUG', 'false') == 'true')


ALLOWED_HOSTS = [
    'servicios.ana-hn.org',
    'www.servicios.ana-hn.org',
    '192.168.10.6',
    '127.0.0.1',
    'localhost',
]

CSRF_TRUSTED_ORIGINS = [
    'https://servicios.ana-hn.org:437',
    'https://192.168.10.6:437',
]

# ─────────────────────────────────────────────────────────────
# 4. APLICACIONES INSTALADAS
# ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Paquetes para personalizar el Admin
    'colorfield',
    'admin_interface',

    # Apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',

    # Apps personalizadas
    'accounts',
    'tickets',
    'inventario',
    'mantenimiento',
    'citas_billingue',
    'citas_colegio',
    'sponsors',
    'menu',
    'enfermeria',
    'seguridad',
    'conducta',
    'core',
   

]


# ─────────────────────────────────────────────────────────────
# 5. MIDDLEWARE
# ─────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ─────────────────────────────────────────────────────────────
# 6. URLS Y WSGI
# ─────────────────────────────────────────────────────────────
ROOT_URLCONF = 'system_proyect.urls'
WSGI_APPLICATION = 'system_proyect.wsgi.application'


# ─────────────────────────────────────────────────────────────
# 7. TEMPLATES
# ─────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.current_year',
            ],
        },
    },
]


# ─────────────────────────────────────────────────────────────
# 8. BASE DE DATOS (MySQL)
# ─────────────────────────────────────────────────────────────
DATABASES = {
    # Base de datos principal (MySQL Workbench → sponsors3)
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'sponsors2'),
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

# ─────────────────────────────────────────────────────────────
# 9. VALIDADORES DE CONTRASEÑAS
# ─────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─────────────────────────────────────────────────────────────
# 10. INTERNACIONALIZACIÓN
# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-hn'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ─────────────────────────────────────────────────────────────
# 11. CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS Y MEDIA
# ─────────────────────────────────────────────────────────────
STATIC_URL = '/static/'

# Lista “bruta” de posibles carpetas static por app
_raw_static_dirs = [
    BASE_DIR / "system_proyect/tickets/static",
    BASE_DIR / "system_proyect/accounts/static",
    BASE_DIR / "system_proyect/inventario/static",
    BASE_DIR / "system_proyect/mantenimiento/static",
    BASE_DIR / "system_proyect/sponsors/static",
    BASE_DIR / "system_proyect/menu/static",
    BASE_DIR / "system_proyect/citas_billingue/static",
    BASE_DIR / "system_proyect/citas_colegio/static",
    BASE_DIR / "system_proyect/static",
]

# Filtra solo las que existen en disco
STATICFILES_DIRS = [
    str(p) for p in _raw_static_dirs
    if p.exists()
]

STATIC_ROOT = BASE_DIR / "staticfiles"



# ─────────────────────────────────────────────────────────────
# 12. ARCHIVOS DE USUARIO (MEDIA)
# ─────────────────────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'





# ──────────────────────────────
# SESIONES Y LOGIN (1 HORA)
# ──────────────────────────────

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/menu/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Duración de la sesión: 1 hora (en segundos)
SESSION_COOKIE_AGE = 60 * 60  # 3600 segundos

# Renovar la sesión con cada request (se reinicia si el usuario navega)
SESSION_SAVE_EVERY_REQUEST = True

# No cerrar la sesión al cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cookies seguras (requerido para HTTPS, déjalo en True si usas HTTPS)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Motor de sesiones recomendado (usa la base de datos cacheada)
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Opcional: Si usas subdominios y quieres que la cookie funcione en todos, descomenta:
# SESSION_COOKIE_DOMAIN = '.ana-hn.org'
# CSRF_COOKIE_DOMAIN = '.ana-hn.org'


# ─────────────────────────────────────────────────────────────
# 13. CORREO ELECTRÓNICO (SMTP)
# ─────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'techcare.app2024@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'dvex nxbf quaj nxtc')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ─────────────────────────────────────────────────────────────
# 14. CAMPO PRIMARY KEY POR DEFECTO
# ─────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─────────────────────────────────────────────────────────────
# 15. URL PARA ADMIN (opcional, por si quieres moverla)
# ─────────────────────────────────────────────────────────────
ADMIN_SITE_URL = '/accounts/login/'

print("DEBUG =", DEBUG)
print("ALLOWED_HOSTS =", ALLOWED_HOSTS)
