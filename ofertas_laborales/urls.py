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
    path("postular/<int:oferta_id>/", views.postular, name="postular"),
    path("postulaciones/", views.listar_postulaciones, name="listar_postulaciones"),
    path('oferta/<int:id_oferta>/postulaciones/', views.ver_postulaciones, name='ver_postulaciones'),
    path('candidato/<int:id_candidato>/', views.ver_perfil_candidato, name='ver_perfil_candidato'),
    path("postulacion/<int:postulacion_id>/entrevista/", views.agendar_entrevista, name="agendar_entrevista"),
    path("entrevista/<int:entrevista_id>/", views.detalle_entrevista, name="detalle_entrevista"),
    path("entrevistas/", views.panel_entrevistas, name="panel_entrevistas"),
]