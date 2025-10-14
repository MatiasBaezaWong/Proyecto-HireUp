from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("registro/", views.registro_candidato, name="registro_candidato"),
    path("login/", views.login_usuario, name="login"),
    path("redirigir/", views.redirigir_por_rol, name="redirigir_por_rol"),
    path("logout/", views.logout_usuario, name="logout"),
]
