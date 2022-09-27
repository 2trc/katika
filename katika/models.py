from django.db import models, connections
from django.db.models.sql.compiler import SQLCompiler
from rest_framework.permissions import BasePermission, SAFE_METHODS


# https://stackoverflow.com/questions/15121093/django-adding-nulls-last-to-query
class NullsLastSQLCompiler(SQLCompiler):
    def get_order_by(self):
        result = super().get_order_by()
        if result and self.connection.vendor == 'postgresql':
            return [(expr, (sql + ' NULLS LAST', params, is_ref))
                    for (expr, (sql, params, is_ref)) in result]
        return result


class NullsLastQuery(models.sql.query.Query):
    """Use a custom compiler to inject 'NULLS LAST' (for PostgreSQL)."""

    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        return NullsLastSQLCompiler(self, connection, using)


class NullsLastQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self.query = query or NullsLastQuery(self.model)


class ReadOnlyOrAdmin(BasePermission):
    '''
    #https://www.django-rest-framework.org/api-guide/permissions/
    '''

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS) or (request.user and request.user.is_staff)


class AbstractTag(models.Model):
    name = models.CharField(max_length=30, null=True)
    name_fr = models.CharField(max_length=30, null=True)

    def __str__(self):

        display_name = ""

        if self.name:
            display_name = self.name

            if self.name_fr:
                display_name += ","

        if self.name_fr:
            display_name += self.name_fr

        return display_name

    class Meta:
        #unique_together = ('name', 'name_fr')
        abstract = True
