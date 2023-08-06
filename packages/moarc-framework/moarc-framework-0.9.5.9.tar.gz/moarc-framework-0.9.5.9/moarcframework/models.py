import json

from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection
from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers
from django.conf import settings

from .orm import fields
from .orm.base_model import BaseModel, CallableModel


class ConfigCategory(BaseModel):

    def _serializer(self):
        return ConfigCategorySerializer

    class Meta:
        db_table = 'base_config_category'
        verbose_name = 'Categoría de Configuración'
        verbose_name_plural = 'Categorías de Configuraciones'

    name = fields.CharField(verbose_name="Nombre")


class ConfigCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigCategory
        fields = ('id', 'name')


class Config(BaseModel):
    def _serializer(self):
        return ConfigSerializer

    class Meta:
        db_table = 'base_config'
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'

    @staticmethod
    def prepared_configs():
        configs = {}
        for config in Config.objects.all():
            configs[config.name] = config.parse_value()
        return configs

    def parse_value(self):
        if self.value in ['True', 'False']:
            return True if self.value == 'True' else False
        if self.data_type == 'number':
            return float(str(self.value))
        if self.is_data_type_record:
            config_value = self.value or 0
            record = apps.get_model(self.record_parameters['model']).objects.filter(pk=config_value).first()
            return record
        return self.value

    @property
    def is_data_type_boolean(self):
        return self.data_type == 'boolean'

    @property
    def is_data_type_record(self):
        return str(self.data_type).startswith('record')

    @property
    def record_parameters(self):
        if self.is_data_type_record:
            parameters = str(self.data_type).split(':', 1)[1].replace("\'", "\"")
            parameter_dict = json.loads(parameters)
            if parameter_dict.get('search_route'):
                parameter_dict['search_url'] = reverse(parameter_dict['search_route'])
            return parameter_dict
        return None

    name = fields.CharField(verbose_name="Nombre")
    description = fields.TextField(verbose_name="Descripción", null=True)
    value = fields.TextField(verbose_name="Valor")
    config_category = fields.ForeignKey(to=ConfigCategory, related_name='configs')
    data_type = fields.TextField(verbose_name="Tipo de dato", default="string")


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = ('id', 'name', 'description', 'value', 'data_type')


class Attachment(BaseModel, CallableModel):
    def _serializer(self):
        return AttachmentSerializer

    class Meta:
        db_table = 'base_attachment'
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'

    @staticmethod
    def get_attachments_from_record(record):
        return Attachment.objects.filter(origin_model_name=record.get_model_label(), origin_model_id=record.id).all()

    name = fields.CharField(verbose_name="Nombre")
    mimetype = fields.CharField(verbose_name="Tipo de archivo")
    size = fields.IntegerField(verbose_name="Tamaño del archivo")
    file = models.FileField(upload_to=getattr(settings, 'MOARC_ATTACHMENT_PATH', 'static/attachments/%Y/%m/%d/'))


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'name', 'file', 'mimetype', 'size')


class Data(models.Model):
    class Meta:
        db_table = 'base_data'
        verbose_name = 'Información de registro'
        verbose_name_plural = 'Información de registro'

    def get_model(self):
        app_label, model_name = str(self.model_name).split('.')
        model_internal_name = str(model_name).replace("_", "")
        model = apps.get_model(app_label=app_label, model_name=model_internal_name)
        return model.objects.filter(pk=self.model_id).first()

    model_name = fields.CharField(verbose_name="Nombre del modelo")
    model_id = fields.IntegerField(verbose_name="ID del modelo")
    identifier = fields.CharField(verbose_name="Identificador")
    created_date = models.DateTimeField(verbose_name="Fecha de creación", default=timezone.now, blank=True, null=True)


class Logbook(CallableModel):
    class Meta:
        db_table = 'base_logbook'
        verbose_name_plural = 'Bitácora'
        verbose_name = 'Bitácora'

    LOGBOOK_IGNORED_FIELDS = ['id', 'created_date', 'updated_date', 'created_by', 'updated_by', 'origin_model_name',
                              'origin_model_id']

    @staticmethod
    def save_model_to_logbook(model, is_new=False):
        logbook = Logbook()
        initial = model.initial
        changes = model.changes
        [initial.pop(field) for field in Logbook.LOGBOOK_IGNORED_FIELDS if field in initial]
        [changes.pop(field) for field in Logbook.LOGBOOK_IGNORED_FIELDS if field in changes]
        logbook.from_changes = str(initial) if not is_new else ''
        logbook.to_changes = str(changes)
        logbook.user_id = model.created_by
        logbook.user_name = model.created_by_name
        logbook.origin_model_id = model.id
        logbook.origin_model_name = model.get_internal_name()
        logbook.save()

    from_changes = fields.TextField(verbose_name="Original", null=True)
    to_changes = fields.TextField(verbose_name="Cambios", null=True)
    created_date = fields.DateTimeField(verbose_name="Fecha de creación", default=timezone.now, blank=True, null=True)
    user_name = fields.CharField(verbose_name="Usuario", null=True)
    user_id = fields.IntegerField(verbose_name="Id del usuario", null=True)


class Menu(BaseModel):
    def _serializer(self):
        return MenuSerializer

    class Meta:
        db_table = 'base_menu'
        verbose_name = 'Menú de navegación'
        verbose_name_plural = 'Menú de navegación'
        ordering = ['sorting_number']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Menu, self).save(force_insert, force_update, using, update_fields)
        if not self.permission:
            self._create_permission_for_menu()

    def _create_permission_for_menu(self):
        permission_name = "{%s} %s" % (self.id, self.name)
        permission_code_name = permission_name.lower().replace(' ', '-')
        content_type = ContentType.objects.get_for_model(self)
        permission = Permission.objects.create(name=permission_name, codename=permission_code_name,
                                               content_type=content_type)
        self.permission = permission
        self.save()

    @property
    def child_menus(self):
        return self.get_menus_by_user_and_parent_menu(parent_menu=self)

    @staticmethod
    def get_menus_by_user_and_parent_menu(user=None, parent_menu=None):
        user_id = user.id if user else None
        parent_menu_id = parent_menu.id if parent_menu else None
        with connection.cursor() as cursor:
            cursor.execute('select * from usp_moarc_get_menus(%s, %s)', [user_id, parent_menu_id])
            rows = cursor.fetchall()
        menus = Menu.objects.filter(pk__in=[row[0] for row in rows], parent_menu=parent_menu).order_by('sorting_number')
        return menus

    @property
    def route_url(self):
        route = None
        try:
            route_parts = str(self.route).split('|')
            route_name = route_parts[0]
            route_args = {}
            for route_part in route_parts[1:]:
                route_arg = route_part.split(':')
                route_args[route_arg[0]] = route_arg[1]
            route = reverse(route_name, kwargs=route_args)
        except:
            pass
        return route

    def user_has_permission(self, user):
        if self.permission:
            return user.has_perm(self.permission.content_type.app_label + '.' + self.permission.codename)
        return True

    name = fields.CharField(verbose_name="Nombre")
    parent_menu = fields.ForeignKey("self", verbose_name="Menú padre", null=True)
    icon = fields.CharField(verbose_name="Icono", blank=True, null=True)
    sorting_number = fields.IntegerField(verbose_name='Número de ordenamiento')
    route = fields.CharField(verbose_name="Ruta", null=True)
    permission = fields.ForeignKey(verbose_name="Grupo", to=Permission)


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'name', 'parent_menu', 'icon', 'sorting_number', 'route', 'route_url')


class UIView(BaseModel):
    def _serializer(self):
        pass

    class Meta:
        db_table = 'base_ui_view'
        verbose_name = 'Vista UI'
        verbose_name_plural = 'Vistas UI'

    name = fields.CharField(verbose_name="Nombre")
    model = fields.CharField(verbose_name="Modelo")
    path = fields.CharField(verbose_name="Ruta")
    content = fields.TextField(verbose_name="Contenido")


class Sequence(BaseModel):

    def _serializer(self):
        return SequenceSerializer

    class Meta:
        db_table = 'base_sequence'
        verbose_name = 'Secuencia'
        verbose_name_plural = 'Secuencias'

    singular_name = 'sequence'
    plural_name = 'sequences'
    search_fields = ['name']
    list_fields = ['name', 'code', 'prefix', 'suffix']

    name = fields.CharField(verbose_name="Nombre")
    code = fields.CharField(verbose_name="Código")
    prefix = fields.CharField(verbose_name="Prefijo", null=True, blank=True)
    suffix = fields.CharField(verbose_name="Sufijo", null=True, blank=True)
    current_number = fields.IntegerField(verbose_name="Número actual", default=1)
    start = fields.IntegerField(verbose_name='Inicio', default=1)
    padding = fields.IntegerField(verbose_name='Fin', default=5)
    increment = fields.IntegerField(verbose_name='Paso', default=1)

    @staticmethod
    def get_next_by_sequence(sequence_code):
        sequence = Sequence.objects.get(code=sequence_code)
        number = str(sequence.current_number).zfill(sequence.padding)
        name_parts = [sequence.prefix, number, sequence.suffix]
        identifier = "".join([name for name in name_parts if name])
        sequence.current_number += sequence.increment
        sequence.save()
        return identifier


class SequenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sequence
        fields = ('id', 'name', 'code', 'prefix', 'suffix')
