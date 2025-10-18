from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.messages import get_messages
from .forms import RegistroCandidatoForm, LoginUsuarioForm
from django.contrib.auth.decorators import login_required

# Create your views here.

#PAGINA HOME
def MainPage(request):
    return render(request, 'main/home.html')

# REGISTRO CANDIDATO
def registro_candidato(request):
    if request.method == "POST":
        form = RegistroCandidatoForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # inicio automático tras registro
            messages.success(request, "Registro exitoso. ¡Bienvenido!")
            return redirect("ofertas_laborales:vista_candidato")
        else:
            messages.error(request, "Hay errores en el formulario. Revísalos abajo.")
    else:
        form = RegistroCandidatoForm()
    return render(request, "main/registro.html", {"form": form})


# LOGIN
def login_usuario(request):
    if request.method == "POST":
        form = LoginUsuarioForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}")
            return redirect("ofertas_laborales:vista_candidato")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginUsuarioForm()
    return render(request, "main/login.html", {"form": form})


# REDIRECCION AUTOMATICA POR ROL
@login_required
def redirigir_por_rol(request):
    rol = getattr(request.user, "rol", None)

    if rol == "candidato":
        return redirect("ofertas_laborales:vista_candidato")
    elif rol == "reclutador":
        return redirect("ofertas_laborales:vista_reclutador")
    elif rol == "administrador":
        return redirect("administrador:portal_administrador")

    messages.error(request, "No se ha identificado correctamente el tipo de usuario.")
    return redirect("login")


# CIERRE DE SESION
def logout_usuario(request):
    logout(request)
    list(get_messages(request))
    request.session.flush()
    messages.info(request, "Sesión cerrada correctamente.")
    return render(request, 'main/login.html')    

