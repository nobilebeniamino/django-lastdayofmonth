# django‑lastdayofmonth

[![PyPI](https://img.shields.io/pypi/v/django-lastdayofmonth.svg)](https://pypi.org/project/django-lastdayofmonth/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-lastdayofmonth.svg)](https://pypi.org/project/django-lastdayofmonth/)
[![CI](https://github.com/nobilebeniamino/django-lastdayofmonth/actions/workflows/ci.yml/badge.svg)](https://github.com/nobilebeniamino/django-lastdayofmonth/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Cross‑database **`LastDayOfMonth`** ORM function for Django.*

Calculate the last calendar day of any month directly in the database, with the same API on **SQLite, PostgreSQL, MySQL/MariaDB and Oracle**.

---

## Installation

```bash
pip install django-lastdayofmonth
```

That’s it — no settings tweaks required.  
Simply import the helper wherever you need it (see **Quick usage** for an example).

---

## Compatibility matrix

| Django version     | Python version | Supported back‑ends                                                 |
| ------------------ | -------------- | ------------------------------------------------------------------- |
| 3.2 LTS → 5.2 LTS  | 3.8 → 3.12     | SQLite, PostgreSQL ≥ 12, MySQL ≥ 5.7 / MariaDB ≥ 10.4, Oracle ≥ 19c |

The library is fully tested in CI across all the combinations above.

---

## Quick usage

```python
from django.db.models import DateField
from django_lastdayofmonth import LastDayOfMonth

# annotate each invoice with the month‑end date of its `issued_date`
Invoice.objects.annotate(
    month_end=LastDayOfMonth("issued_date")
)
```

`LastDayOfMonth` works in **`annotate()`**, **`filter()`**, **`aggregate()`**, etc.

---

## Why?

Calculating month‑end boundaries in Python causes heavy data transfer and breaks query optimisations.  Leveraging the database engine keeps logic in SQL and stays performant.

---

## Running tests locally

```bash
pip install tox pytest pytest-django dj-database-url mysqlclient oracledb psycopg2-binary  # install testing and DB driver dependencies
pytest -q --reuse-db                 # run tests locally
```

Use `tox` to run the full matrix (`tox -p auto`). See `.github/workflows/ci.yml` for Docker examples of each database.

---

## License

Released under the **MIT** license. See the [LICENSE](LICENSE) file for details.
