# -*- coding: utf-8 -*-
from rest_framework import serializers


class GenericSerializer(serializers.ModelSerializer):

    class Meta:
        model = None
        fields = '__all__'