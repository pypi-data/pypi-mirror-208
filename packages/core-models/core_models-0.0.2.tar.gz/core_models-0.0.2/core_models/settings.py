import os, sys

from dotenv import load_dotenv
from datetime import timedelta

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

AUTH_USER_MODEL = 'app.User'

SECRET_KEY = 'da)(@*#Uhubjindu*(!@#$#@nfoinond-ahp*nen2@=*u)!g8m9pthdg'

INSTALLED_APPS = ['daphne']

CORE_APPS = [
    'storages',
    'cities_light',
    'django_slack',
    'core_models',
    'core_models.app',
]


def db(key):
    return os.getenv(key)


def get_env(key, default=None):
    return os.getenv(key, default)


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': "django.db.backends.sqlite3",
            'NAME': "test.db"
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': db("DB_ENGINE"),
            'NAME': db('POSTGRES_DB'),
            'USER': db('POSTGRES_USER'),
            'PASSWORD': db('POSTGRES_PASSWORD'),
            'HOST': db('DB_HOST'),
            'PORT': db('DB_PORT'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


#######################
# LOCALIZATION CONFIG #
#######################
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


###############
# MAIL CONFIG #
###############
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = os.path.join(PACKAGE_DIR, 'emails')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'admin@liquify.digital'
EMAIL_HOST_PASSWORD = 'vscqwkljfchpkzln'
DEFAULT_FROM_EMAIL = get_env('DEFAULT_FROM_EMAIL', 'Liquify<admin@liquify.digital>')
SERVER_EMAIL = 'Liquify<admin@liquify.digital>'
EMAIL_PORT = 587
# Gmail SMTP port (TLS): 587
# Gmail SMTP port (SSL): 465
EMAIL_USE_TLS = True
EMAIL_SIGNATURE = 'The Liquify Team'
ADMINS = (
    ('Fola', 'fola@liquify.digital'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

#################
# LOGGER CONFIG #
#################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] %(asctime)s %(name)s: %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'slack_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django_slack.log.SlackExceptionHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'handlers': ['console', ],
        'level': 'DEBUG'
    },
    'loggers': {
        'django.request': {
            'handlers': [
                'console', 'mail_admins'
            ],
            'level': 'DEBUG',
            'propagate': True
        },
        'django': {
            'level': 'ERROR',
            'handlers': ['slack_admins'],
            'propagate': True
        },
    }
}
#####################
# SAFEDELETE CONFIG #
#####################
SAFE_DELETE_FIELD_NAME = "deleted_at"
SAFE_DELETE_CASCADED_FIELD_NAME = "deleted_by_id"

##############
# DRF CONFIG #
##############
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 15,
    'PAGINATE_BY_PARAM': 'limit',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

##############
# JWT CONFIG #
##############
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=12),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

CORS_ALLOW_ALL_ORIGINS = True
REDIS_CONFIG_KEY = "CONFIGURATIONS"

####################
# ONESIGNAL CONFIG #
####################
ONE_SIGNAL_APP_ID = get_env("ONE_SIGNAL_APP_ID")
ONE_SIGNAL_REST_API_KEY = get_env("ONE_SIGNAL_REST_API_KEY")
ONE_SIGNAL_USER_AUTH_KEY = get_env("ONE_SIGNAL_USER_AUTH_KEY")


################
# SLACK CONFIG #
################
SLACK_TOKEN = get_env("SLACK_BOT_TOKEN")
SLACK_CHANNEL = get_env("SLACK_CHANNEL")
SLACK_USERNAME = get_env("SLACK_BOT_USERNAME")


################
# MEDIA CONFIG #
################
FILE_UPLOAD_STORAGE = get_env("FILE_UPLOAD_STORAGE", default="local")  # local | s3

if FILE_UPLOAD_STORAGE == "local":
    MEDIA_ROOT_NAME = "media"
    MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_ROOT_NAME)
    MEDIA_URL = f"/{MEDIA_ROOT_NAME}/"

if FILE_UPLOAD_STORAGE == "s3":
    # Using django-storages
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_AUTO_CREATE_BUCKET = True
    AWS_S3_ACCESS_KEY_ID = get_env("AWS_S3_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = get_env("AWS_S3_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = get_env("AWS_STORAGE_BUCKET_NAME", "liquify-media-v1-3di3n")
    AWS_S3_REGION_NAME = get_env("AWS_S3_REGION_NAME")
    AWS_S3_SIGNATURE_VERSION = get_env("AWS_S3_SIGNATURE_VERSION", default="s3v4")

    # https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl
    AWS_DEFAULT_ACL = get_env("AWS_DEFAULT_ACL", default="public-read")

    AWS_PRESIGNED_EXPIRY = int(get_env("AWS_PRESIGNED_EXPIRY", default='10'))  # seconds
