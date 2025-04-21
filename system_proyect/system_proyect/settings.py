import os
from dotenv import load_dotenv
from pathlib import Path

# 1. Cargar las variables del archivo .env
load_dotenv()

# 2. Paths y base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. Django Secret Key & Debug
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-b(q9vw0wc#j2@pxe-kl4+(nbi0p4lth&t&nc7vy2a-*m01v!fq')
DEBUG = (os.getenv('DJANGO_DEBUG', 'True') == 'True')

# 4. Hosts permitidos
ALLOWED_HOSTS = []

# 5. Aplicaciones instaladas
INSTALLED_APPS = [
    # Apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps personalizadas
    'accounts',
    'tickets',
    'inventario',
    'mantenimiento',
    'citas_billingue',
    'citas_colegio',
    'sponsors',
    'menu',
]

# 6. Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 7. Root URL y WSGI
ROOT_URLCONF = 'system_proyect.urls'
WSGI_APPLICATION = 'system_proyect.wsgi.application'

# 8. Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Plantillas globales
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

# 9. Ajustes de Admin
ADMIN_SITE_URL = '/accounts/login/'

# 10. Configuración de sesiones e inactividad
SESSION_COOKIE_AGE = 600  # 10 minutos
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 11. Configuración de la base de datos (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'sponsors2'),
        'USER': os.getenv('DB_USER', 'admin3'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'Test-12345'),
        'HOST': os.getenv('DB_HOST', '192.168.10.6'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}

# 12. Configuración de login y logout
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/menu/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# 13. Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'techcare.app2024@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'dvex nxbf quaj nxtc')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 14. Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 15. Internacionalización
LANGUAGE_CODE = 'ES-HN'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 16. Archivos estáticos (CSS, JS, Imágenes)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "system_proyect/tickets/static",
    BASE_DIR / "system_proyect/inventario/static",
    BASE_DIR / "system_proyect/mantenimiento/static",
    BASE_DIR / "system_proyect/sponsors/static",
    BASE_DIR / "system_proyect/menu/static",
    BASE_DIR / "system_proyect/citas_billingue/static",
    BASE_DIR / "system_proyect/citas_colegio/static",
    BASE_DIR / "system_proyect/static",  # carpeta general
]

# Ruta donde se almacenarán los archivos estáticos recolectados por collectstatic
STATIC_ROOT = BASE_DIR / "staticfiles"


# 17. Primary key por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
