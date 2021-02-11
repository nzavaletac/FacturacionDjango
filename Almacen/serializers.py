from django.db.models import fields
from rest_framework import serializers
from .models import InventarioModel


class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventarioModel
        # Los campos como PK(autofield) solamente será de solo lectura
        fields = '__all__'  # Voy a usar por completo todas las columnas del modelo inventario
        # fields = ['inventarioPlato', ]
        # Solamente puedo usar el exclude o el fields
        # esclude = ['inventarioId']


class PlatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventarioModel
        fields = ['inventarioPlato']
