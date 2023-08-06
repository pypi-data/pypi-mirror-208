# -*- coding: utf-8 -*-
from abc import abstractmethod

from django.apps import apps
from django.core.cache import cache
from django.db import models
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from ..helpers.auth import Auth
from ..helpers.paginator import Paginator
from ..http.generic_serializer import GenericSerializer

ADMIN_USER_ID = 1

BASE_FIELDS = ['id', 'created_date', 'updated_date', 'created_by', 'updated_by', 'origin_model_name',
               'origin_model_id']
IMPORT_ELEMENT_INPUT_NAME = 'import'

FILTERS_STRATEGIES = {
    '=': '__exact',
    'like': '__icontains',
    '>=': '__gte',
    '<=': '__lte',
    'in': '__in',

}


class BaseModel(models.Model):
    record_name = 'name'

    class Meta:
        ordering = 'id desc'
        abstract = True

    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    def save(self, *args, **kwargs):
        is_new = self.is_new
        self._set_created_by()
        self._set_updated_by()
        super(BaseModel, self).save(*args, **kwargs)
        self.__initial = self._dict
        # TODO: Enable logbook by config
        # apps.get_model('moarcframework', 'logbook').save_model_to_logbook(self, is_new)

    def fill_model(self, values: dict):
        fields = self.get_fields_as_dict()
        for key in values.keys():
            if hasattr(self, key) and fields.get(key):
                setattr(self, key, values[key])
        return self

    def get_model_label(self):
        return self._meta.label

    def get_fields_as_dict(self):
        fields = self._meta.get_fields(include_hidden=False, include_parents=False)
        dict_fields = {}
        for field in fields:
            if hasattr(field, 'attname'):
                dict_fields[field.attname] = field
        return dict_fields

    def clone(self):
        self.pk = None
        return self

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    @property
    def is_new(self):
        return not bool(self.id)

    @property
    def initial(self):
        return self.__initial

    @property
    def changes(self):
        return self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                                           self._meta.fields])

    def _set_created_by(self):
        current_user = Auth.get_current_user()
        if hasattr(self, 'created_by') and self.is_new:
            if current_user:
                self.created_by = current_user.id
            else:
                self.created_by = ADMIN_USER_ID

    def _set_updated_by(self):
        if hasattr(self, 'updated_by') and not self.is_new:
            current_user = Auth.get_current_user()
            self.updated_date = timezone.now()
            if current_user:
                self.updated_by = current_user.id
            else:
                self.updated_by = ADMIN_USER_ID

    @property
    def created_by_name(self):
        user = apps.get_model('base', 'user').objects.filter(pk=self.created_by).first()
        return user.username if user else ''

    @property
    def updated_by_name(self):
        user = apps.get_model('base', 'user').objects.filter(pk=self.updated_by).first()
        return user.username if user else ''

    def store(self, values, request):
        self.fill_model(values)
        self._on_store(values, request)
        self.save()
        self._on_stored(values, request)
        response = {
            'success': True
        }
        return JsonResponse(response)

    def update(self, values, request):
        model = self.__class__.objects.get(pk=values.get('id'))
        model.fill_model(values)
        model._on_update(values, request)
        model.save()
        model._on_updated(values, request)
        response = {
            'success': True
        }
        return JsonResponse(response)

    def toggle_active(self, values, request):
        model = self.__class__.objects.get(pk=request.GET['id'])
        model.active = not model.active
        model.save()
        response = {
            'success': True
        }
        return JsonResponse(response)

    def search(self, values, request):
        records = self._filter(request, values)
        if request.content_type == 'application/json':
            records = self._apply_dynamic_filters(records, values)
        data = Paginator.paginate(records.all(), values, self._serializer(), self)
        return JsonResponse(data, safe=False)

    def show(self, values, request):
        model = self.__class__.objects.get(pk=request.GET['id'])
        response = {
            'record': self._serializer()(model, many=False).data
        }
        return JsonResponse(response)

    def list(self, values, request):
        model_template = self._find_template()
        response = {
            'table': model_template['table'],
            'search': model_template['search'],
            'func_name': 'list'
        }
        return render(request, 'framework/ui/table.html', self._prepare_response_for_templates(response))

    def create(self, values, request):
        response = {
            'form': self._find_template()['form'],
            'func_name': 'store'
        }
        return render(request, 'framework/ui/form.html', self._prepare_response_for_templates(response))

    def edit(self, values, request):
        model = self.__class__.objects.get(pk=request.GET['id'])
        response = {
            'form': model._find_template()['form'],
            'func_name': 'update'
        }
        return render(request, 'framework/ui/form.html', model._prepare_response_for_templates(response))

    def show_import_form(self, values, request):
        response = {
            'import_view': self._find_template()['import'],
        }
        return render(request, 'framework/ui/import.html', self._prepare_response_for_templates(response))

    def _on_stored(self, values, request):
        pass

    def _on_updated(self, values, request):
        pass

    def _on_store(self, values, request):
        pass

    def _on_update(self, values, request):
        pass

    def _find_template(self):
        cache_key = 'uiview.' + self.get_model_label()  # TODO: apply cache view
        template = apps.get_model('base', 'uiview').objects.filter(model=self.get_model_label()).first()
        parsed_content = eval(template.content)
        cache.set(cache_key, parsed_content)
        return parsed_content

    @abstractmethod
    def _serializer(self):
        pass

    def _filter(self, request, values):
        records = self.__class__.objects.filter()
        if values is dict and 'active' not in values:
            records = records.filter(active=True)
        return records

    @staticmethod
    def _apply_dynamic_filters(records, request_post):
        kwargs = {}
        for condition in request_post.get('filters', []):
            type_for_py = FILTERS_STRATEGIES.get(condition['type'], '=')
            filter_key = '{0}{1}'.format(condition['field'], type_for_py)
            kwargs[filter_key] = condition['value'] if condition['type'] == 'in' else str(condition['value'])
        return records.filter(**kwargs) if kwargs else records

    def _prepare_response_for_templates(self, args: dict = None):
        response = {
            'model': {
                'class': self.__class__,
                'self': self,
                'singular_name': 'record',
                'label': self.get_model_label(),
                'verbose_name_singular': self._meta.verbose_name,
                'verbose_name_plural': self._meta.verbose_name_plural,
            }}
        if args:
            response.update(args)
        return response

    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(verbose_name="Fecha de creación", default=timezone.now, blank=True, null=True)
    updated_date = models.DateTimeField(verbose_name="Fecha de actualización", blank=True, null=True)
    created_by = models.IntegerField(verbose_name="Creado por", null=True)
    updated_by = models.IntegerField(verbose_name="Actualizado por", null=True)


class CallableModel(models.Model):
    class Meta:
        abstract = True

    origin_model_name = models.TextField(verbose_name="Modelo de origen", blank=True, null=True)
    origin_model_id = models.TextField(verbose_name="Id del modelo de origen", blank=True, null=True)
