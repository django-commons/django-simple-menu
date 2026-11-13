import os

TEST_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tests")

INSTALLED_APPS = ["simple_menu"]

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(TEST_DIR, "static")

SECRET_KEY = "testing-menus-is-so-much-fun"

# LOGGING = {
#     "version": 1,  # the dictConfig format version
#     "disable_existing_loggers": False,  # retain the default loggers
#     "handlers": {
#         "console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#         },
#     },
#     "loggers": {
#         "simple_menu": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#         },
#     },
# }

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(TEST_DIR, "test_templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
