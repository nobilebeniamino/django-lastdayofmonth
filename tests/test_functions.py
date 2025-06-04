"""tests/test_functions.py

A comprehensive test‑suite for ``django_lastdayofmonth.LastDayOfMonth``.

Goals
-----
* Verify that the ORM annotation returns the correct last calendar day for
  both ``DateField`` and ``DateTimeField`` expressions.
* Check behaviour with ``NULL`` values and common edge‑cases (first / last
  day of a month, leap years).
* Ensure the generated SQL is appropriate for every officially supported
  backend (SQLite, PostgreSQL, MySQL/MariaDB, Oracle).

The tests run without migrations: an in‑memory model is built on‑the‑fly
using ``isolate_apps`` so the package can be tested in any Django project
or CI matrix without configuring extra apps.

Requires ``pytest`` and ``pytest‑django``.
"""

from __future__ import annotations

import datetime as dt
import uuid

import pytest
from django.apps import AppConfig
from django.db import connection, models
from django.db.models import DateField, DateTimeField, F, Func, Value
from django.test.utils import isolate_apps

from django_lastdayofmonth import LastDayOfMonth

# ---------------------------------------------------------------------------
# 1. Dynamic model definition (no migrations)
# ---------------------------------------------------------------------------


class _ModelAppConfig(AppConfig):
    """Lightweight app config used by ``isolate_apps`` below."""

    label = "model_app"
    name = "tests.test_functions"


@isolate_apps("tests.test_functions")
def _build_invoice_model():
    """Return an unmanaged model with date/datetime columns for testing."""

    class Invoice(models.Model):
        guid = models.UUIDField(default=uuid.uuid4)
        issued_date = models.DateField(null=True)
        issued_ts = models.DateTimeField(null=True)

        class Meta:
            app_label = "model_app"
            managed = False  # skip migrations

    return Invoice


Invoice = _build_invoice_model()

# ---------------------------------------------------------------------------
# 2. Helper utilities
# ---------------------------------------------------------------------------


def _compile(expr: Func) -> str:
    """Compile a Django expression to raw SQL for the current connection."""

    compiler_cls = connection.ops.compiler("SQLCompiler")
    compiler = compiler_cls(None, connection, None)
    sql, _ = compiler.compile(expr) 
    return sql


# ---------------------------------------------------------------------------
# 3. Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def invoice(db):
    """Create a single Invoice row with a leap‑year date for edge‑case tests."""

    return Invoice.objects.create(
        issued_date=dt.date(2024, 2, 5),
        issued_ts=dt.datetime(2024, 2, 5, 12, 0),
    )


# ---------------------------------------------------------------------------
# 4. Functional tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_datefield_annotation(invoice):
    qs = Invoice.objects.annotate(month_end=LastDayOfMonth("issued_date")).values_list(
        "month_end", flat=True
    )
    assert qs.get() == dt.date(2024, 2, 29)


@pytest.mark.django_db
def test_datetimefield_annotation(invoice):
    qs = Invoice.objects.annotate(month_end=LastDayOfMonth("issued_ts")).values_list(
        "month_end", flat=True
    )
    assert qs.get() == dt.date(2024, 2, 29)


@pytest.mark.django_db
def test_null_handling(db):
    obj = Invoice.objects.create(issued_date=None, issued_ts=None)

    result = (
        Invoice.objects.filter(pk=obj.pk)
        .annotate(month_end=LastDayOfMonth("issued_date"))
        .values_list("month_end", flat=True)
        .get()
    )
    assert result is None


@pytest.mark.parametrize(
    "input_date, expected",
    [
        (dt.date(2025, 1, 15), dt.date(2025, 1, 31)),
        (dt.date(2025, 4, 10), dt.date(2025, 4, 30)),
        (dt.date(2025, 2, 28), dt.date(2025, 2, 28)),  # already month‑end
    ],
)
@pytest.mark.django_db
def test_various_months(db, input_date, expected):
    obj = Invoice.objects.create(
        issued_date=input_date,
        issued_ts=dt.datetime.combine(input_date, dt.time.min),
    )
    result = (
        Invoice.objects.filter(pk=obj.pk)
        .annotate(month_end=LastDayOfMonth("issued_date"))
        .values_list("month_end", flat=True)
        .get()
    )
    assert result == expected


# ---------------------------------------------------------------------------
# 5. Backend‑specific SQL tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sql_generation_backend():
    sample_date = dt.date(2025, 5, 17)
    expr = LastDayOfMonth(Value(sample_date, output_field=DateField()))
    sql = _compile(expr)

    vendor = connection.vendor
    if vendor == "sqlite":
        assert "date(" in sql and "+1 month" in sql and "-1 day" in sql
    elif vendor == "postgresql":
        assert "date_trunc" in sql and "interval '1 day'" in sql
    elif vendor in {"mysql", "mariadb"}:
        assert "LAST_DAY" in sql
    elif vendor == "oracle":
        assert "LAST_DAY" in sql
    else:
        pytest.skip(f"Backend '{vendor}' not covered by the test‑suite")


@pytest.fixture(scope="session", autouse=True)
def _install_invoice_table(django_db_setup, django_db_blocker):
    """
    Create table `model_app_invoice` out of any transaction,
    so it can be used in SQLite.
    """
    with django_db_blocker.unblock():
        # fuori dalle transazioni di pytest-django
        with connection.schema_editor(atomic=False) as schema:
            schema.create_model(Invoice)

    yield

    # smontiamo a fine suite (facoltativo, ma pulito)
    with django_db_blocker.unblock():
        with connection.schema_editor(atomic=False) as schema:
            schema.delete_model(Invoice)