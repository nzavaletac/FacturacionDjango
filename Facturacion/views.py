from rest_framework import generics, status
from .models import CabeceraComandaModel, ComprobanteModel, MesaModel
from .serializers import CierreDiaSerializer, ComandaDetalleSerializer, ComprobanteSerializer, CustomPayloadSerializer, DevolverNotaSerializer, GenerarComprobanteSerializer, InicioConsumidorSerializer, RegistroSerializer, MesaSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import SoloCajeros, SoloMeseros
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from .generarComprobante import emitirComprobante
from datetime import datetime


class RegistroUsuarioView(generics.CreateAPIView):
    serializer_class = RegistroSerializer

    def post(self, request):
        nuevoUsuario = self.serializer_class(data=request.data)
        nuevoUsuario.is_valid(raise_exception=True)
        nuevoUsuario.save()
        return Response({
            'ok': True,
            'content': nuevoUsuario.data
        }, status=201)


class CustomPayloadView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomPayloadSerializer


class MesasView(generics.ListCreateAPIView):
    queryset = MesaModel.objects.all()
    serializer_class = MesaSerializer
    # Este es e atributo que va a regir en toda mi view y va a permitir o denegar ciertos acceso
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated, SoloCajeros]

    def get(self, request):
        resultado = self.serializer_class(
            instance=self.get_queryset(), many=True)
        print(resultado.data)
        return Response({
            'ok': True,
            'content': resultado.data,
            'message': None
        })

    def post(self, request):
        nuevaMesa = self.serializer_class(data=request.data)
        print(nuevaMesa.initial_data)
        nuevaMesa.is_valid(raise_exception=True)
        # print(nuevaMesa.data)
        nuevaMesa.save()
        return Response({
            'ok': True,
            'content': nuevaMesa.data,
            'message': 'Se creó la mesa exitosamente'
        }, status=status.HTTP_201_CREATED)

# Controlador en el cual me muestre las mesas disponibles
# Se usa mas un apiview cunado nosotros tengamos que usar un método (GET, POST, PUT) y así nos evitaremos de crear una clase con todos sus atributos


@api_view(['GET'])
@permission_classes([IsAuthenticated, SoloCajeros])
def mesas_disponibles(request):
    # Usar el serializado MesaSerializer
    # Hacer una búsqueda de todas las mesas con estado true
    # Retornar ese resultado
    mesas = MesaModel.objects.filter(mesaEstado=True).all()
    resultadoSerializado = MesaSerializer(instance=mesas, many=True)
    return Response({
        'ok': True,
        'content': resultadoSerializado.data,
        'message': None
    })
    # Retornar ese resultado


class ComandasViews(generics.ListCreateAPIView):
    serializer_class = InicioConsumidorSerializer

    def post(self, request):
        resultado = InicioConsumidorSerializer(data=request.data)
        resultado.is_valid(raise_exception=True)
        resultado.save()
        return Response({
            'ok': True,
            'message': 'Se creó la comanda exitosamente.',
            'content': None
        })

    def get(self, request):
        pass


class CrearPedidoView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, SoloMeseros]
    serializer_class = ComandaDetalleSerializer

    def post(self, request):
        resultado = self.serializer_class(data=request.data)
        resultado.is_valid(raise_exception=True)
        resultado.save()
        return Response({
            'ok': True,
            'content': resultado.data
        })


class GenerarNotaPedidoView(generics.ListAPIView):
    serializer_class = DevolverNotaSerializer
    queryset = CabeceraComandaModel.objects.all()

    def get_queryset(self, id):
        cabecera = self.queryset.filter(cabeceraId=id).first()
        # cabecera.cabeceraEstado = 'CERRADO'
        # cabecera.save()
        return cabecera

    def get(self, request, id_comanda):
        # Al momwnto de hacer la petición de la comanda se tiene que cambiar su estado a CERRADO
        cabecera = self.get_queryset(id_comanda)
        cabecera.cabeceraEstado = 'CERRADO'
        cabecera.save()
        # OJO: Al momento de devolver la lista, ya debe aparecer con el estado CERRADO
        resultado = self.serializer_class(
            instance=self.get_queryset(id_comanda))
        return Response({
            'ok': True,
            'content': resultado.data
        })


class GenerarComprobantePago(generics.ListCreateAPIView):
    serializer_class = GenerarComprobanteSerializer

    def get(self, request, id_comanda):
        return Response({
            'ok': True
        })

    def post(self, request, id_comanda):
        resultado = self.serializer_class(data=request.data)
        if resultado.is_valid():
            tipo_comprobante = resultado.validated_data.get(
                'tipo_comprobante')
            cliente_tipo_documento = resultado.validated_data.get(
                'cliente_tipo_documento')
            cliente_documento = resultado.validated_data.get(
                'cliente_documento')
            cliente_email = resultado.validated_data.get('cliente_email')
            observaciones = resultado.validated_data.get('observaciones')
            verificacion = ComprobanteModel.objects.filter(
                cabecera=id_comanda).first()
            if verificacion:
                comprobante = ComprobanteSerializer(instance=verificacion)
                return Response({
                    'ok': False,
                    'content': comprobante.data,
                    'message': 'Ya existe un comprobante para esa comanda,'
                }, status=status.HTTP_400_BAD_REQUEST)
            respuesta = emitirComprobante(tipo_comprobante,
                                          cliente_tipo_documento,
                                          cliente_documento,
                                          cliente_email,
                                          id_comanda,
                                          observaciones)
            if respuesta.get('errors'):
                return Response({
                    'ok': False,
                    'content': respuesta.get('errors'),
                    'message': 'Hubo un error al crear el comprobante.'
                })
            else:
                print(respuesta)
                serie = respuesta.get('serie')
                numero = respuesta.get('numero')
                tipo = respuesta.get('tipo_de_comprobante')
                cliente = cliente_documento
                pdf = respuesta.get('enlace_del_pdf')
                xml = respuesta.get('enlace_del_xml')
                cdr = respuesta.get('enlace_del_cdr')
                cabecera = CabeceraComandaModel.objects.get(
                    cabeceraId=id_comanda)
                nuevoComprobante = ComprobanteModel(comprobanteSerie=serie,
                                                    comprobanteNumero=numero,
                                                    comprobanteTipo=tipo,
                                                    comprobanteCliIdentificacion=cliente,
                                                    comprobantePdf=pdf,
                                                    comprobanteCdr=cdr,
                                                    comprobanteXML=xml,
                                                    cabecera=cabecera)
                nuevoComprobante.save()
                comprobanteSerializado = ComprobanteSerializer(
                    instance=nuevoComprobante)
                return Response({
                    'ok': True,
                    'content': comprobanteSerializado.data,
                    'message': 'Comprobante creado exitosamente.'
                })
        else:
            return Response({
                'ok': False,
                'content': resultado.errors,
                'message': 'Hubo un error al generar el comprobante.'
            })
        pass


@ api_view(['POST'])
# Crear un permission para solamente un mesero pueda registrar un pedido
# @permission_classes([IsAuthenticated, SoloMeseros])
def crear_pedido(request):
    return Response('NO SIRVE')


class CierreDiaView(generics.ListAPIView):
    serializer_class = CierreDiaSerializer

    def get(self, request):
        fecha_actual = datetime.now()
        comandas = CabeceraComandaModel.objects.filter(
            cabeceraFecha=fecha_actual).all()
        comandaSerializada = self.serializer_class(
            instance=comandas, many=True)
        return Response({
            'ok': True,
            'content': comandaSerializada.data,
            'message': None
        })
