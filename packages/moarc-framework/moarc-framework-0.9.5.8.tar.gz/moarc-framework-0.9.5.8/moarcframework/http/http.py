# -*- coding: utf-8 -*-
import json

from django.apps import apps
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .decorators import action
from django.conf import settings


@action
@csrf_exempt
@transaction.atomic
def process_model_func(request, model_id, func_name):
    if request.content_type == 'text/plain' and not request.user.is_authenticated:
        return redirect(_get_redirect_url())
    app_name, model_name = str(model_id).split('.')
    model_class = apps.get_model(app_name, model_name)
    request_content = request.body
    if request.content_type == 'application/json':
        request_content = json.loads(request.body)
    # TODO Protect internal functions
    return getattr(model_class(), func_name)(request_content, request)


def _get_redirect_url():
    LOGIN_REDIRECT_ROUTE_NAME = getattr(settings, 'LOGIN_REDIRECT_ROUTE_NAME', 'login')
    redirect_url = reverse(LOGIN_REDIRECT_ROUTE_NAME)
    return redirect_url
