import os
import dj_database_url

SECRET_KEY = "dummy"
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django_lastdayofmonth",
]

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///:memory:"
    )
}