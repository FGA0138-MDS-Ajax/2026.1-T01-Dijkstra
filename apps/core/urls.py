from django.urls import path
from apps.core.controllers.home_controller import home
from apps.core.controllers.eventos_controller import (EventosController,event_list_controller,)

urlpatterns = [
    path('', home, name='home'),
    path('eventos/', EventosController.as_view(), name='eventos-list'),
    path('eventos/<int:evento_id>/', EventosController.as_view(), name='eventos-detail'),
    path('eventos-filtro/', event_list_controller, name='eventos-filtro'),
]