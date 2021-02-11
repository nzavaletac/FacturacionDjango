from django.urls import path
from .views import InventariosView, InventarioView

urlpatterns = [
    path("inventario", InventariosView.as_view()),
    path("inventario/<int:inventario_id>", InventarioView.as_view())
]
