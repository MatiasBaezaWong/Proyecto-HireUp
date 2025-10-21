from django.shortcuts import render, redirect, get_object_or_404
from main.decorators import role_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import EditarCandidatoForm, CustomPasswordChangeForm, CrearOfertaForm
from main.models import OfertaLaboral, Postulacion
from datetime import datetime
from django.http import JsonResponse

# Create your views here.

#VISTA CANDIDATO
@role_required("candidato")
def vista_candidato(request):
    
    ofertas = OfertaLaboral.objects.all().order_by('-fecha_publicacion')
    return render(request, "ofertas_laborales/ofertas_candidato.html", {

    "ofertas": ofertas,

})

#VISTA RECLUTADOR
@role_required("reclutador")
def vista_reclutador(request):

    reclutador = request.user.perfil_reclutador
    ofertas = OfertaLaboral.objects.all().filter(reclutador=reclutador).order_by('-fecha_publicacion')
    return render(request, "ofertas_laborales/ofertas_reclutador.html", {

    "reclutador": reclutador,
    "ofertas": ofertas,

})    

#PERFIL CANDIDATO
@login_required
@role_required("candidato")
def perfil_candidato(request):
    candidato = request.user.perfil_candidato
    usuario = request.user

    if request.method == "POST":
        if 'update_info' in request.POST:
            form = EditarCandidatoForm(request.POST, request.FILES, instance=candidato)
            pass_form = CustomPasswordChangeForm(request.user)
            if form.is_valid():
                form.save()
                nuevo_email = form.cleaned_data.get("email")
                if nuevo_email and nuevo_email != usuario.email:
                    usuario.email = nuevo_email
                    usuario.save()

                messages.success(request, "Perfil actualizado correctamente.")
                return redirect("ofertas_laborales:perfil_candidato")
            else:
                messages.error(request, "Por favor corrige los errores del formulario.")
        elif 'change_password' in request.POST:
            form = EditarCandidatoForm(instance=candidato)
            pass_form = CustomPasswordChangeForm(request.user, request.POST)
            if pass_form.is_valid():
                user = pass_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña cambiada exitosamente.")
                return redirect("ofertas_laborales:perfil_candidato")
            else:
                messages.error(request, "Error al cambiar la contraseña.")
    else:
        initial_data = {'email': usuario.email}
        form = EditarCandidatoForm(instance=candidato, initial=initial_data)
        pass_form = CustomPasswordChangeForm(request.user)

    return render(request, "ofertas_laborales/perfil_candidato.html", {
        "form": form,
        "pass_form": pass_form,
    })

#PERFIL RECLUTADOR
@login_required
@role_required("reclutador")
def perfil_reclutador(request):
    reclutador = request.user.perfil_reclutador
    return render(request, "ofertas_laborales/perfil_reclutador.html", {"reclutador": reclutador})

# CREACION OFERTA LABORAL (SOLO PARA RECLUTADORES)
@login_required
@role_required("reclutador")
def crear_oferta(request):
    reclutador = request.user.perfil_reclutador

    if request.method == "POST":
        form = CrearOfertaForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.reclutador = reclutador
            oferta.save()
            messages.success(request, "Oferta publicada con éxito.")
            return redirect("ofertas_laborales:vista_reclutador")
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = CrearOfertaForm()

    return render(request, "ofertas_laborales/crear_oferta.html", {"form": form})       

#VOLVER A PAGINA HOME
def volver_home(request):
    return redirect('home')        

# EDITAR OFERTA LABORAL (SOLO PARA RECLUTADORES)
@login_required
@role_required("reclutador")
def editar_oferta(request, oferta_id):
    oferta = get_object_or_404(OfertaLaboral, id=oferta_id, reclutador=request.user.perfil_reclutador)
    if request.method == "POST":
        form = CrearOfertaForm(request.POST, instance=oferta)
        if form.is_valid():
            form.save()
            messages.success(request, "Oferta actualizada con éxito.")
            return redirect("ofertas_laborales:vista_reclutador")
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = CrearOfertaForm(instance=oferta)
    return render(request, "ofertas_laborales/editar_oferta.html", {"form": form, "oferta": oferta})

# ELIMINAR OFERTA LABORAL (SOLO PARA RECLUTADORES)
@login_required
@role_required("reclutador")
def eliminar_oferta(request, oferta_id):
    oferta = get_object_or_404(OfertaLaboral, id=oferta_id, reclutador=request.user.perfil_reclutador)
    if request.method == "POST":
        oferta.delete()
        messages.success(request, "Oferta eliminada con éxito.")
        return redirect("ofertas_laborales:vista_reclutador")
    return render(request, "ofertas_laborales/eliminar_oferta.html", {"oferta": oferta})


# DETALLE OFERTA LABORAL
def detalle_oferta(request, oferta_id):
    oferta = get_object_or_404(OfertaLaboral, id=oferta_id)
    return render(request, "ofertas_laborales/detalle_oferta.html", {"oferta": oferta})

# POSTULAR A OFERTA LABORAL
@login_required
@role_required("candidato")
def postular(request, oferta_id):
    try:
        # Obtener la oferta
        oferta = get_object_or_404(OfertaLaboral, id=oferta_id)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al obtener la oferta: {str(e)}'})

    candidato = request.user.perfil_candidato

    # Verificar si ya está postulado
    try:
        if Postulacion.objects.filter(candidato=candidato, oferta=oferta).exists():
            return JsonResponse({'success': False, 'message': 'Ya te has postulado a esta oferta.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al verificar postulación: {str(e)}'})

    # Verificar el estado de la oferta
    try:
        if oferta.estado == "cerrada":
            return JsonResponse({'success': False, 'message': 'La oferta se encuentra cerrada.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al verificar postulación: {str(e)}'})    

    # Crear la postulación
    try:
        reclutador = oferta.reclutador  # Asumimos que la oferta tiene un reclutador asignado
        postulacion = Postulacion.objects.create(
            candidato=candidato,
            oferta=oferta,
            reclutador=reclutador
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al guardar la postulación: {str(e)}'})
