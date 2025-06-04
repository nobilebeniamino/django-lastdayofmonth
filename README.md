# django-lastdayofmonth

[![PyPI](https://img.shields.io/pypi/v/django-lastdayofmonth.svg)](https://pypi.org/project/django-lastdayofmonth/)
[![Tests](https://github.com/beniaminonobile/django-lastdayofmonth/actions/workflows/ci.yml/badge.svg)](https://github.com/beniaminonobile/django-lastdayofmonth/actions)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-lastdayofmonth)](https://pypi.org/project/django-lastdayofmonth/)

*A cross‑database `LastDayOfMonth` ORM function for Django.*

---

## Motivation

Calculating the last calendar day of a month is a common requirement for:

* payroll cut‑offs  
* month‑end KPI dashboards  
* fiscal or accounting reports  

Without this helper you either hand‑roll vendor‑specific SQL or subclass `django.db.models.Func` in every project.  
**django‑lastdayofmonth** gives you **one import** that works on all official Django back‑ends.

---

## Installation

```bash
pip install django-lastdayofmonth
```

No settings, no project tweaks, no extra apps.

---

## Quick start

```python
from django_lastdayofmonth import LastDayOfMonth
from invoices.models import Invoice

invoices = (
    Invoice.objects
    .annotate(period_end=LastDayOfMonth("issued_at"))
    .values("issued_at", "period_end")
)
```

* `period_end` is a plain `date` containing the month’s last day.  
* Works with **`DateField`** *and* **`DateTimeField`** expressions.  
* Plays nicely with `filter()`, `annotate()`, `aggregate()`, etc.

---

## What SQL is generated?

| Backend         | SQL emitted                                                               |
|-----------------|---------------------------------------------------------------------------|
| PostgreSQL      | `date_trunc('month', exp + interval '1 month') - interval '1 day'`        |
| MySQL / MariaDB | `LAST_DAY(exp)`                                                           |
| SQLite          | `date(exp, '+1 month', 'start of month', '-1 day')`                       |
| Oracle          | `LAST_DAY(exp)`                                                           |

*MySQL/MariaDB and Oracle expose `LAST_DAY()` natively, so the helper is essentially zero‑cost on those engines.*

---

## Compatibility

| Django        | Python   | Back‑ends                                                                       |
|---------------|----------|---------------------------------------------------------------------------------|
| 3.2 LTS → 4.2 | 3.8–3.10 | SQLite, PostgreSQL ≥ 12, MySQL ≥ 5.7 / MariaDB ≥ 10.4, Oracle ≥ 19c             |

Tested continuously in CI via **tox** & GitHub Actions.

---

## Contributing

Pull‑requests and bug reports are welcome!

```bash
git clone https://github.com/beniaminonobile/django-lastdayofmonth.git
cd django-lastdayofmonth
pip install -e .[dev]      # optional extras: pytest, tox, black…
tox                        # runs the full test matrix
```

Please include tests for new logic—see `tests/test_functions.py` for examples.

---

## Changelog

See **CHANGELOG.md** for released versions.

---

## License

Licensed under the MIT License—see **LICENSE** for details.