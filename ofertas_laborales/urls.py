from django.urls import path
from . import views

app_name = "ofertas_laborales"

urlpatterns = [
    path("candidato/", views.vista_candidato, name="vista_candidato"),
    path("perfil/", views.perfil_candidato, name="perfil_candidato"),
    path("perfil-rec/", views.perfil_reclutador, name="perfil_reclutador"),
    path("reclutador/", views.vista_reclutador, name="vista_reclutador"),
    path("crear-oferta/", views.crear_oferta, name="crear_oferta"),
    path('volver-home/', views.volver_home, name='volver_home'),
    path("editar_oferta/<int:oferta_id>/", views.editar_oferta, name="editar_oferta"),
    path("eliminar_oferta/<int:oferta_id>/", views.eliminar_oferta, name="eliminar_oferta"),
    path('detalle/<int:oferta_id>/', views.detalle_oferta, name='detalle_oferta'),
    path("postular/<int:oferta_id>/", views.postular, name="postular")
]