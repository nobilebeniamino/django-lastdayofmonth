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

# Hack for MySQL/MariaDB and Oracle
if DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
    DATABASES["default"]["TEST"] = {"NAME": DATABASES["default"]["NAME"]}
elif DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
    DATABASES["default"]["TEST"] = {
        "USER": DATABASES["default"]["USER"],
        "TBLSPACE": "USERS",
        "TBLSPACE_TMP": "TEMP",
        "MIRROR": None,
        "KEEPDB": True,
    }