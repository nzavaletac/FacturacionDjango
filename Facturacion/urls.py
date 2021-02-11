from django.urls import path
from .views import CierreDiaView, ComandasViews, CrearPedidoView, CustomPayloadView, GenerarComprobantePago, GenerarNotaPedidoView, MesasView, RegistroUsuarioView, crear_pedido, mesas_disponibles
# Validas las credenciales y sí estas son correctas me retornará al JWT
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('registro', RegistroUsuarioView.as_view()),
    # path('login', TokenObtainPairView.as_view()),
    path('login', CustomPayloadView.as_view()),
    path('mesa', MesasView.as_view()),
    path('mesasDisponibles', mesas_disponibles),
    path('comanda', ComandasViews.as_view()),
    path('crearPedido', CrearPedidoView.as_view()),
    path('crearPedidoDeprecated', crear_pedido),
    path('notaPedido/<int:id_comanda>', GenerarNotaPedidoView.as_view()),
    path('comprobante/<int:id_comanda>', GenerarComprobantePago.as_view()),
    path('cierreDia', CierreDiaView.as_view())

]
