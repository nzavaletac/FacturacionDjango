from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    info=openapi.Info(
        title='Facturacion de Restaurantes con SUNAT',
        default_version='v1',
        description='API del manejo de un restaurante con facturción',
        term_of_service='https://www.google.com',
        contact=openapi.Contact(
            email='nzavaletac@gmail.com', name='Noe Zavaleta Cardeña'),
        license=openapi.License(name='MIT')
    ),
    public=True,
    permission_classes=(AllowAny,)

)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0)),
    path('admin/', admin.site.urls),
    path('almacen/', include('Almacen.urls')),
    path('facturacion/', include('Facturacion.urls')),
]
