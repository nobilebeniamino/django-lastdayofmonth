from django.db.models import Func, DateField

class LastDayOfMonth(Func):
    """
    Return the last calendar day of the month for the given date expression.
    Usage:
        from django_lastdayofmonth import LastDayOfMonth
        MyModel.objects.annotate(month_end=LastDayOfMonth("my_date"))
    """
    output_field = DateField()
    arity = 1
    function = "LAST_DAY"          # usato da MySQL/MariaDB/Oracle

    def as_mysql(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, **extra_context)

    as_mariadb = as_mysql
    as_oracle = as_mysql

    def as_postgresql(self, compiler, connection, **extra_context):
        expr = self.get_source_expressions()[0]
        # date_trunc('month', d + interval '1 month') - interval '1 day'
        return compiler.compile(
            Func(
                Func(expr, function="date_trunc",
                     template="date_trunc('month', %(expressions)s + interval '1 month')"),
                function=None,
                template="%(expressions)s - interval '1 day'",
                output_field=self.output_field,
            )
        )

    def as_sqlite(self, compiler, connection, **extra_context):
        expr = self.get_source_expressions()[0]
        # date(d, '+1 month', 'start of month', '-1 day')
        return compiler.compile(
            Func(
                expr,
                function=None,
                template="date(%(expressions)s, '+1 month','start of month','-1 day')",
                output_field=self.output_field,
            )
        )