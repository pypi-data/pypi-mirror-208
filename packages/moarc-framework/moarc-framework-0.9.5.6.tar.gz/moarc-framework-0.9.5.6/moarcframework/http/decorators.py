# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from functools import wraps

from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError


def action(function=None, mandatory=True, **ajax_kwargs):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            try:
                return func(request, *args, **kwargs)
            except ValidationError as exception:
                message = "\r\n".join(exception.detail)
                return JsonResponse({'response': message}, status=status.HTTP_400_BAD_REQUEST)

        return inner

    if function:
        return decorator(function)
    return decorator
