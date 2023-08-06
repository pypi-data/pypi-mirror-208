from rest_framework.response import Response

PER_PAGE = 20
from rest_framework.pagination import PageNumberPagination


class Object(object):
    pass


class Paginator:

    @staticmethod
    def prepare_paginate_parameters(request):
        request_parameters = request if request is dict else {}
        paginate_parameters = {
            'order_field': request_parameters.get('sorters')[0]['field'] if request_parameters.get('sorters') else None,
            'order_direction': request_parameters.get('sorters')[0]['dir'] if request_parameters.get(
                'sorters') else None,
            'per_page': int(request_parameters.get('size', PER_PAGE)),
            'page': 1 if not request_parameters.get('page') else int(request_parameters.get('page'))
        }
        return paginate_parameters

    @staticmethod
    def paginate(query_set, request, serializer=None, model=None):
        paginate_parameters = Paginator.prepare_paginate_parameters(request)
        order_field = paginate_parameters['order_field']
        order_direction = paginate_parameters['order_direction']
        order = Paginator.__get_pagination_order(order_field, order_direction, model)
        if order:
            query_set = query_set.order_by(order)
        per_page = paginate_parameters['per_page']  # Change param in frontend
        page = paginate_parameters['page']
        from_results = 0 if page == 1 else page * per_page - per_page
        to_results = from_results + per_page
        total_records = len(query_set)
        total_pages = round(total_records / per_page) if total_records else 0
        results = query_set[from_results:to_results]
        serializer = serializer(results, many=True)
        return {
            'page': page,
            'pages': total_pages,
            'from': from_results,
            'to': to_results,
            'total': total_records,
            'results': serializer.data
        }

    @staticmethod
    def __get_pagination_order(order_field, order_direction, model):
        if order_field:
            if order_direction == 'asc':
                return '-' + order_field
            return order_field
        if model._meta.ordering:
            return model._meta.ordering[0]
        return '-id'
