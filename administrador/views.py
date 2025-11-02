from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .forms import RegistroReclutadorForm, EditarReclutadorForm, EditarCandidatoForm, ObraForm
from main.models import Usuario, Reclutador, Candidato, Obra

# Create your views here.

# PORTAL ADMINISTRADOR
@login_required
def portal_administrador(request):
    # Restringir acceso solo a administradores
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado")

    # Formulario de creación de reclutador
    if request.method == "POST":
        form = RegistroReclutadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reclutador creado con éxito.")
            return redirect("administrador:portal_administrador")
    else:
        form = RegistroReclutadorForm()

    # Listar todos los usuarios existentes
    reclutadores = Reclutador.objects.select_related("usuario").all()
    candidatos = Candidato.objects.select_related("usuario").all()
    usuarios = Usuario.objects.all().select_related()

    return render(request, "administrador/portal_administrador.html", {
        "form": form,
        "usuarios": usuarios,
        "reclutadores": reclutadores,
        "candidatos": candidatos,
    })

# EDITAR RECLUTADOR
@login_required
def editar_reclutador(request, pk):
    # Restringir acceso solo a administradores
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado")

    reclutador = get_object_or_404(Reclutador, pk=pk)

    # Formulario de edicion del reclutador
    if request.method == "POST":
        form = EditarReclutadorForm(request.POST, instance=reclutador)
        if form.is_valid():
            form.save()
            messages.success(request, "Reclutador actualizado correctamente.")
            return redirect("administrador:portal_administrador")
        else:
            messages.error(request, "Hay errores en el formulario.")
    else:
        form = EditarReclutadorForm(instance=reclutador)

    return render(request, "administrador/editar_reclutador.html", {
    "form": form,
    "reclutador": reclutador,
})

# ELIMINAR RECLUTADOR
@login_required
def eliminar_reclutador(request, pk):
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado")

    reclutador = get_object_or_404(Reclutador, pk=pk)
    usuario = reclutador.usuario

    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Reclutador eliminado correctamente.")
        return redirect("administrador:portal_administrador")

    return redirect("administrador:portal_administrador")  

# EDITAR CANDIDATO
@login_required
def editar_candidato(request, pk):
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado")

    candidato = get_object_or_404(Candidato, pk=pk)

    if request.method == "POST":
        form = EditarCandidatoForm(request.POST, instance=candidato)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidato actualizado correctamente.")
            return redirect("administrador:portal_administrador")
        else:
            messages.error(request, "Hay errores en el formulario.")
    else:
        form = EditarCandidatoForm(instance=candidato)

    return render(request, "administrador/editar_candidato.html", {
    "form": form,
    "candidato": candidato,
})

# ELIMINAR CANDIDATO
@login_required
def eliminar_candidato(request, pk):
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado")

    candidato = get_object_or_404(Candidato, pk=pk)
    usuario = candidato.usuario

    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Candidato eliminado correctamente.")
        return redirect("administrador:portal_administrador")

    return redirect("administrador:portal_administrador")

@login_required
def gestionar_obras(request):
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado.")

    obras = Obra.objects.select_related("comuna__ciudad__region").all()

    return render(request, "administrador/gestionar_obras.html", {
        "obras": obras
    })


@login_required
def crear_obra(request):
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado.")

    if request.method == "POST":
        form = ObraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Obra registrada correctamente.")
            return redirect("administrador:gestionar_obras")
    else:
        form = ObraForm()

    return render(request, "administrador/crear_obra.html", {"form": form})    

# VOLVER AL HOME
def volver_home(request):
    return redirect('home')    