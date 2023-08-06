from sqlglot import parse_one, exp

from django.core import exceptions as django_exceptions
from . import exceptions
from django.db.models import Value, Q, F
from django.db.models.lookups import (Exact, IContains, GreaterThan, LessThan,
    GreaterThanOrEqual, LessThanOrEqual, In, IsNull)


class Parser:

    def __init__(self, model, database='postgres', date_format='%Y-%m-%d'):
        self.query = None
        self.model = model
        self.date_format = date_format
        self.database = database
        # extraparams to keep information on Cone-queries and required aliases
        self.extra_params = dict(cones=[], aliases=dict())

    def parse(self, query):
        """
        Parse SQL-like WHERE clause and return Django Q objects which can be 
        used in Model.objects.filter()
        """

        self.query = query
        parsed = parse_one(query, read=self.database)
        return self._resolve(parsed)

    def _resolve(self, p):
        """Resolve SQLglot expression tree to Q objects and F aliases"""

        # lets go from simple to complex structures
        if isinstance(p, exp.Literal):
            if p.is_string:
                return Value(p.this)
            elif p.is_int:
                return Value(int(p.this))
            elif p.is_number:
                return Value(float(p.this))
            else:
                raise exceptions.InvalidLiteral()

        elif isinstance(p, exp.Column):
            if p.this.quoted:
                # This is the case of double quoted string parsed as column identifier in SQL.
                # It is not assumed to use double quotes in the column name.
                return Value(p.this.this)
            else:
                return self._resolve_column(p)

        elif isinstance(p, exp.Neg):
            return -self._resolve(p.this)

        elif isinstance(p, exp.Not):
            return ~Q(self._resolve(p.this))

        elif isinstance(p, exp.Paren):
            # return ExpressionWrapper(self._resolve(p.this), None)
            return self._resolve(p.this)

        # Logical operators
        elif isinstance(p, exp.And):
            return Q(self._resolve(p.left)) & Q(self._resolve(p.right))

        elif isinstance(p, exp.Or):
            return Q(self._resolve(p.left)) | Q(self._resolve(p.right))

        # Comparison operators
        elif isinstance(p, exp.EQ):
            return Exact(self._resolve(p.left), self._resolve(p.right))

        elif isinstance(p, exp.Is):
            if isinstance(p.right, exp.Null):
                return IsNull(self._resolve(p.left), True)
            else:
                return Exact(self._resolve(p.left), self._resolve(p.right))

        elif isinstance(p, exp.NEQ):
            return ~Exact(self._resolve(p.left), self._resolve(p.right))

        elif isinstance(p, exp.GT):
            return GreaterThan(self._resolve(p.left), self._resolve(p.right))

        elif isinstance(p, exp.LT):
            return LessThan(self._resolve(p.left), self._resolve(p.right))

        elif isinstance(p, exp.GTE):
            return GreaterThanOrEqual(self._resolve(p.left), self._resolve(p.right))

        elif isinstance(p, exp.LTE):
            return LessThanOrEqual(self._resolve(p.left), self._resolve(p.right))

        elif isinstance(p, exp.RegexpLike):
            return IContains(self._resolve(p.this), self._resolve(p.expression))

        # Math operators
        elif isinstance(p, exp.Add):
            return self._resolve(p.left) + self._resolve(p.right)

        elif isinstance(p, exp.Sub):
            return self._resolve(p.left) - self._resolve(p.right)

        elif isinstance(p, exp.Mul):
            return self._resolve(p.left) * self._resolve(p.right)

        elif isinstance(p, exp.Div):
            return self._resolve(p.left) / self._resolve(p.right)

        # Special operators
        elif isinstance(p, exp.Between):
            return GreaterThanOrEqual(self._resolve(p.this), self._resolve(p.args['low'])) & \
                   LessThanOrEqual(self._resolve(p.this), self._resolve(p.args['high']))

        elif isinstance(p, exp.In):
            return In(self._resolve(p.this), [self._resolve(r) for r in p.expressions])

        else:
            raise exceptions.InvalidQuery()

    def _resolve_column(self, p):
        """Resolve column.
        Related fields are possible but less than 3 nested levels.
        f1.f2.f3.f4 - should be still valid. But only two embedded levels have been tested.
        """
        model = self.model

        parts = p.parts

        while len(parts) > 1:
            # iterate over all nested levels
            current_identifier = parts.pop(0)
            model = model._meta.get_field(current_identifier.this).related_model

        try:
            # check field name existence
            model._meta.get_field(parts[0].this)

            full_field_name = "__".join([part.this for part in p.parts])
            return F(full_field_name)
        except django_exceptions.FieldDoesNotExist:
            raise exceptions.FieldDoesNotExist(parts[0].this)
