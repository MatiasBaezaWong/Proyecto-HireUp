from django.urls import path
from . import views

app_name = "administrador"

urlpatterns = [
    path("portal/", views.portal_administrador, name="portal_administrador"),
    path("panel_usuarios/", views.panel_usuarios, name="panel_usuarios"),
    path("panel_postulacion/", views.panel_postulacion, name="panel_postulacion"),
    path("crear_reclutador/", views.crear_reclutador, name="crear_reclutador"),
    path("exportar_usuarios_excel/", views.exportar_usuarios_excel, name="exportar_usuarios_excel"),
    path("informe_pdf/", views.generar_informe_pdf, name="generar_informe_pdf"),
    path("editar-reclutador/<int:pk>/", views.editar_reclutador, name="editar_reclutador"),
    path("editar-candidato/<int:pk>/", views.editar_candidato, name="editar_candidato"),
    path('eliminar-candidato/<int:pk>/', views.eliminar_candidato, name='eliminar_candidato'),
    path('eliminar-reclutador/<int:pk>/', views.eliminar_reclutador, name='eliminar_reclutador'),
    path("obras/", views.gestionar_obras, name="gestionar_obras"),
    path("obras/nueva/", views.crear_obra, name="crear_obra"),
    path("ajax/cargar-ciudades/", views.cargar_ciudades, name="ajax_cargar_ciudades"),
    path("ajax/cargar-comunas/", views.cargar_comunas, name="ajax_cargar_comunas"),
    path("panel-ofertas/", views.panel_ofertas, name="panel_ofertas"),
    path('volver-home/', views.volver_home, name='volver_home')
]