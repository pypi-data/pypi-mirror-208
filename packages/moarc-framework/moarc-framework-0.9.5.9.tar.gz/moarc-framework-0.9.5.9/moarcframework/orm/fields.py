# -*- coding: utf-8 -*-
from django.db import models

BLANK = True
NULL = True
MAX_LENGTH_CHAR_FIELD = 200
MAX_LENGTH_TEXT_FIELD = 500


class CharField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = kwargs.get('blank', BLANK)
        kwargs['null'] = kwargs.get('null', NULL)
        kwargs['default'] = kwargs.get('default', '')
        kwargs['max_length'] = kwargs.get('max_length', MAX_LENGTH_CHAR_FIELD)
        super().__init__(*args, **kwargs)


class BooleanField(models.BooleanField):

    def __init__(self, **kwargs):
        kwargs['null'] = kwargs.get('null', NULL)
        super().__init__(**kwargs)


class IntegerField(models.IntegerField):
    _default = 0

    def __init__(self, **kwargs):
        kwargs['default'] = kwargs.get('default', self._default)
        super().__init__(**kwargs)


class DateField(models.DateField):

    def __init__(self, **kwargs):
        kwargs['null'] = kwargs.get('null', NULL)
        super().__init__(**kwargs)


class DateTimeField(models.DateTimeField):

    def __init__(self, **kwargs):
        kwargs['null'] = kwargs.get('null', NULL)
        super().__init__(**kwargs)


class DecimalField(models.DecimalField):
    _default = 0.0
    _decimal_places = 2
    _max_digits = 10

    def __init__(self, **kwargs):
        kwargs['default'] = kwargs.get('default', self._default)
        kwargs['decimal_places'] = kwargs.get('decimal_places', self._decimal_places)
        kwargs['max_digits'] = kwargs.get('max_digits', self._max_digits)
        super().__init__(**kwargs)


class FloatField(models.FloatField):

    def __init__(self, **kwargs):
        kwargs['null'] = kwargs.get('null', NULL)
        kwargs['blank'] = kwargs.get('blank', BLANK)
        super().__init__(**kwargs)


class ForeignKey(models.ForeignKey):

    def __init__(self, to, **kwargs):
        kwargs['null'] = kwargs.get('null', NULL)
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        super().__init__(to, **kwargs)


class TimeField(models.TimeField):

    def __init__(self, **kwargs):
        kwargs['null'] = kwargs.get('null', NULL)
        kwargs['blank'] = kwargs.get('blank', BLANK)
        super().__init__(**kwargs)


class TextField(models.TextField):

    def __init__(self, *args, **kwargs):
        kwargs['default'] = kwargs.get('default', '')
        kwargs['null'] = kwargs.get('null', NULL)
        kwargs['max_length'] = kwargs.get('max_length', MAX_LENGTH_TEXT_FIELD)
        super().__init__(*args, **kwargs)
