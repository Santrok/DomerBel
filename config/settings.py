from pathlib import Path
import os
from dotenv import dotenv_values

env_keys = dotenv_values()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env_keys.get('DJANGO_TOKEN')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '217.197.116.151']

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.postgres',

    'drf_yasg',
    'drf_recaptcha',
    'debug_toolbar',
    'rest_framework',
    'corsheaders',
    'django_dump_load_utf8',
    'django_ckeditor_5',

    'channels',

    'mptt',
    'django_recaptcha',
    'django_filters',

    'main_page_domer',
    'users',
    'advertisement',
    'api_domer',
    'chat',
    'paid_service',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'advertisement.context_processors.get_date_today',
                'advertisement.context_processors.get_data_category_and_region',
                'config.context_processor.get_context_data',
                'main_page_domer.context_processor.get_data_about_organization',
            ],
        },
    },
]

SITE_ID = 2

WSGI_APPLICATION = 'config.wsgi.application'

# Настройка для пагинатора
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,  # Лимит на количество элементов на странице
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env_keys.get('POSTGRES_DB_NAME'),
        'USER': env_keys.get('DB_USERNAME'),
        'PASSWORD': env_keys.get('DB_PASSWORD'),
        'HOST': env_keys.get('DB_HOST'),
        'PORT': env_keys.get('DB_PORT'),
    }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Minsk'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # используется при деплое

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = [
    "127.0.0.1",

]

CORS_ALLOW_ALL_ORIGINS = True

AUTH_USER_MODEL = 'users.User'

LOGIN_REDIRECT_URL = 'users/personal_account/'
LOGIN_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # Для отображения писем в консоли
EMAIL_BACKEND = env_keys.get("EMAIL_BACKEND")
EMAIL_HOST_PASSWORD = env_keys.get("EMAIL_HOST_PASSWORD")
EMAIL_HOST = env_keys.get("EMAIL_HOST")
EMAIL_PORT = env_keys.get("EMAIL_PORT")
EMAIL_HOST_USER = env_keys.get("EMAIL_HOST_USER")
EMAIL_USE_SSL = env_keys.get("EMAIL_USE_SSL")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER

# Настройки капчи
CAPTCHA_FONT_SIZE = 40
CAPTCHA_FONT_PATH = 'main_page_domer/static/fonts/arial/arial.ttf'
CAPTCHA_CHALLENGE_FUNCT = 'users.captcha.random_digit_challenge'  # Функция для генерации CAPTCHA на русском языке

RECAPTCHA_PUBLIC_KEY = env_keys.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env_keys.get('RECAPTCHA_PRIVATE_KEY')
DRF_RECAPTCHA_SECRET_KEY = env_keys.get('RECAPTCHA_PRIVATE_KEY')

# настройки CELERY
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
# Используем redbeat для планирования задач CELERY BEAT
CELERY_REDBEAT_REDIS_URL = "redis://localhost:6379/2"
RED_BEAT_REDIS_URL = "redis://localhost:6379/2"
CELERY_BEAT_SCHEDULER = 'redbeat.RedBeatScheduler'

# CKEditor==============
customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]

CKEDITOR_5_CUSTOM_CSS = 'django_ckeditor_5/admin_dark_mode_fix.css'  # optional
CKEDITOR_5_FILE_STORAGE = "main_page_domer.functions.CkeditorCustomStorage"  # optional
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'png', 'jpg', "gif", "bmp", "webp", "tiff"]
CKEDITOR_5_IMAGE_BACKEND = "pillow"
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
        'language': 'ru',

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                    'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable', ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        },
        'language': 'ru',
    },
    'extends2': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                    'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing',
                    'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'removeFormat',
                    ],
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        },
        'language': 'ru',
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}
# Celery settings
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"

ASGI_APPLICATION = "config.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": env_keys.get('CHANNEL_LAYERS_BACKEND'),
        # "CONFIG": {
        #     "hosts": [("127.0.0.1", 6379)],
        # },
    }
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
