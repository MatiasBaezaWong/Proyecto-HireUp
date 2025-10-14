from django.urls import path
from . import views

app_name = "administrador"

urlpatterns = [
    path("portal/", views.portal_administrador, name="portal_administrador"),
    path("editar/<int:pk>/", views.editar_reclutador, name="editar_reclutador"),
    path("editar-candidato/<int:pk>/", views.editar_candidato, name="editar_candidato"),
    path('eliminar-candidato/<int:pk>/', views.eliminar_candidato, name='eliminar_candidato'),
    path('eliminar/<int:pk>/', views.eliminar_reclutador, name='eliminar_reclutador'),
    path('volver-home/', views.volver_home, name='volver_home')
]