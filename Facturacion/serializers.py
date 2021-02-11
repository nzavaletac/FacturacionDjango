from django.db.models import fields
from rest_framework import serializers
from rest_framework.utils import model_meta
from .models import ComprobanteModel, DetalleComandaModel, UsuarioModel, MesaModel, CabeceraComandaModel
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# Hora horaria establecidad e el sttings
from django.utils import timezone
# Hora del servidor
# from time import timezone
from Almacen.serializers import PlatoSerializer


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def save(self):
        usuarioCorreo = self.validated_data.get('usuarioCorreo')
        usuarioNombre = self.validated_data.get('usuarioNombre')
        usuarioApellido = self.validated_data.get('usuarioApellido')
        usuarioTipo = self.validated_data.get('usuarioTipo')
        password = self.validated_data.get('password')
        nuevoUsuario = UsuarioModel(
            usuarioCorreo=usuarioCorreo,
            usuarioNombre=usuarioNombre,
            usuarioApellido=usuarioApellido,
            usuarioTipo=usuarioTipo
        )
        nuevoUsuario.set_password(password)
        nuevoUsuario.save()
        return nuevoUsuario

    class Meta:
        model = UsuarioModel
        # fields = '__all__'
        exclude = ['groups', 'user_permissions']


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MesaModel
        fields = '__all__'


class CustomPayloadSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(CustomPayloadSerializer, cls).get_token(user)
        # Luego que ya tenemos definida la token con el padre, podemos agregar nuevos elementos
        token['nombreCompleto'] = user.usuarioNombre+user.usuarioApellido
        token['usuarioTipo'] = user.usuarioTipo
        return token


class InicioConsumidorSerializer(serializers.Serializer):
    mesaId = serializers.IntegerField()
    meseroId = serializers.IntegerField()

    def save(self):
        """Acá se guardará la cebecera"""
        print(self.validated_data)
        mesaId = self.validated_data.get('mesaId')
        meseroId = self.validated_data.get('meseroId')
        # PASO 1: Cambiar el estado de la mesa según su id
        # Comando para devolver la mesa según su ID
        # UPDATE t_mesa SET mesa_estado=0 where mesa_id=mesaId
        # la clausula update me retornará el total de registros actualizados
        # Si deseo solamente con el filter
        mesa2 = MesaModel.objects.filter(mesaId=mesaId)
        mesa2.update(mesaEstado=False)
        print(mesa2[0])
        # Si uso el método first ya no podré usar el método update puesto que solo funciona cunado hay un array de instancias
        mesa = MesaModel.objects.filter(mesaId=mesaId).first()
        # Para actualiza uno o varios
        # mesa = MesaModel.objects.filter(mesaId=mesaId).update(mesaEstado=False)
        # El método solo funciona cuando queremos actualizar uno o varios registros
        # mesa.update(mesaEstado=False)
        mesa.mesaEstado = False
        mesa.save()
        print(mesa)
        mesero = UsuarioModel.objects.filter(usuarioId=meseroId).first()
        print(mesero)
        # PASO 2: Crear la cabecera de la comanda con la mes y el mesero
        nuevaCabecera = CabeceraComandaModel(cabeceraFecha=timezone.now(
        ), cabeceraTotal=0.0, cabeceraCliente="", mesa=mesa, usuario=mesero)
        nuevaCabecera.save()
        return nuevaCabecera


class ComandaDetalleSerializer(serializers.ModelSerializer):
    def save(self):
        # Aparte de registrar la comanda hacer el descuento del inventario
        cantidad = self.validated_data.get('detalleCantidad')
        subtotal = self.validated_data.get('detalleSubtotal')
        cabecera = self.validated_data.get('cabecera')
        inventario = self.validated_data.get('inventario')
        detalleComanda = DetalleComandaModel(detalleCantidad=cantidad, detalleSubtotal=subtotal,
                                             cabecera=cabecera, inventario=inventario)
        detalleComanda.save()
        # Cuando usamos un modelSerializer todas las fk internamente el serializador hace la busqueda antes de validar
        print(inventario)
        inventario.inventarioCantidad = inventario.inventarioCantidad-cantidad
        inventario.save()
        totalDetalle = subtotal*cantidad
        cabecera.cabeceraTotal = cabecera.cabeceraTotal+totalDetalle
        # print(cabecera)
        # print(cabecera.cabeceraTotal)
        # save() => Se guarda los datos en la bd
        cabecera.save()
        return detalleComanda

    class Meta:
        model = DetalleComandaModel
        fields = '__all__'


class MeseroSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioModel
        fields = ['usuarioNombre', 'usuarioApellido']


class DevolverNotaDetalleSerializer(serializers.ModelSerializer):
    plato = PlatoSerializer(source='inventario')

    class Meta:
        model = DetalleComandaModel
        # fields = '__all__'
        exclude = ['inventario', 'cabecera', 'detalleId']


class DevolverNotaSerializer(serializers.ModelSerializer):
    detalleComanda = DevolverNotaDetalleSerializer(
        source='cabeceraDetalles', many=True)
    mesero = MeseroSerializer(source='usuario')
    # usuario = MeseroSerializer()

    class Meta:
        model = CabeceraComandaModel
        # fields = '__all__'
        exclude = ['usuario']


class GenerarComprobanteSerializer(serializers.Serializer):
    tipo_comprobante = serializers.IntegerField()
    cliente_tipo_documento = serializers.CharField(max_length=3)
    cliente_documento = serializers.CharField(max_length=11)
    cliente_email = serializers.CharField(max_length=50)
    observaciones = serializers.CharField(max_length=255)


class ComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComprobanteModel
        fields = '__all__'


class CierreDiaSerializer(serializers.ModelSerializer):
    mesa = MesaSerializer()
    mozo = MeseroSerializer(source='usuario')
    detalle = DevolverNotaDetalleSerializer(
        source='cabeceraDetalles', many=True)
    comprobante = ComprobanteSerializer(source='comanda_cabecera')

    class Meta:
        model = CabeceraComandaModel
        fields = '__all__'
