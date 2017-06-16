from rest_framework import pagination
from rest_framework.response import Response
from collections import OrderedDict

# https://medium.com/@jonasrenault/setting-up-pagination-with-angularjs-and-django-rest-framework-4acadd4b787a
# Create your models here.
class Pagination(pagination.PageNumberPagination):

    def get_paginated_response(self, data):

        range_min = max(1, self.page.number - 3)

        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.page_size),
            ('page', self.page.number),
            ('num_pages', self.page.paginator.num_pages),
            ('range_min', range_min),
            ('range_max', min(self.page.paginator.num_pages, range_min + 6)),


            ('results', data)
        ]))

        #response = super(Pagination, self).get_paginated_response(data)



        #return response
