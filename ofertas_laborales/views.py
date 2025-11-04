from django.shortcuts import render, redirect, get_object_or_404
from main.decorators import role_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import EditarCandidatoForm, CustomPasswordChangeForm, CrearOfertaForm, EntrevistaForm
from main.models import OfertaLaboral, Postulacion, Ciudad, Obra, Candidato, Comuna, Entrevista
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
import requests
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

#VISTA CANDIDATO
@role_required("candidato")
def vista_candidato(request):

    ofertas = OfertaLaboral.objects.select_related('obra', 'reclutador').all()
    comunas = Comuna.objects.all().order_by("nombre").distinct()
    obras = Obra.objects.all().order_by("nombre").distinct()
    areas = OfertaLaboral.objects.values_list("area", flat=True).distinct()

    # Obtener los parámetros del formulario
    keyword = request.GET.get("keyword")
    obra = request.GET.get("obra")
    ubicacion = request.GET.get("ubicacion")
    experiencia = request.GET.get("experiencia")
    area = request.GET.get("area")

    # Filtro dinámico
    filtros = Q()

    if keyword:
        filtros &= (
            Q(titulo__icontains=keyword)
            | Q(cargo__icontains=keyword)
            | Q(descripcion__icontains=keyword)
            | Q(requisitos__icontains=keyword)
        )
    if obra:
        filtros &= Q(obra__nombre__icontains=obra)
    if ubicacion:
        filtros &= (
            Q(obra__comuna__nombre__icontains=ubicacion)
            | Q(obra__comuna__ciudad__nombre__icontains=ubicacion)
            | Q(obra__comuna__ciudad__region__nombre__icontains=ubicacion)
        )
    if experiencia:
        try:
            experiencia = int(experiencia)
            filtros &= Q(experiencia_minima__lte=experiencia)
        except ValueError:
            pass
    if area:
        filtros &= Q(area__iexact=area)

    # Aplicar los filtros
    ofertas = ofertas.filter(filtros).distinct().order_by("-fecha_publicacion", "-id")

    paginator = Paginator(ofertas, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "ofertas_laborales/ofertas_candidato.html", {

    "page_obj": page_obj,
    "ofertas": ofertas,
    "comunas": comunas,
    "obras": obras,
    "areas": areas,
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

# DESCARGAR CV
@login_required
def descargar_cv(request, candidato_id):
    try:
        candidato = Candidato.objects.get(id=candidato_id)
        if not candidato.cv:
            raise Http404("No hay CV disponible")

        response = requests.get(candidato.cv)
        if response.status_code != 200:
            raise Http404("Error al obtener el archivo desde Supabase")

        filename = f"{candidato.nombre}_{candidato.apellido}_CV.pdf"
        content_type = response.headers.get("Content-Type", "application/octet-stream")

        download_response = HttpResponse(response.content, content_type=content_type)
        download_response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return download_response

    except Candidato.DoesNotExist:
        raise Http404("Candidato no encontrado")   

# DESCARGAR CV (VISTA RECLUTADOR)
def descargar_cv_reclutador(request, candidato_id):
    try:
        candidato = Candidato.objects.get(id=candidato_id)
        if not candidato.cv:
            raise Http404("No hay CV disponible")

        # Descargar desde Supabase
        response = requests.get(candidato.cv)
        if response.status_code != 200:
            raise Http404("Error al obtener el archivo desde Supabase")

        filename = f"{candidato.nombre}_{candidato.apellido}_CV.pdf"
        content_type = response.headers.get("Content-Type", "application/pdf")

        download_response = HttpResponse(response.content, content_type=content_type)
        download_response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return download_response

    except Candidato.DoesNotExist:
        raise Http404("Candidato no encontrado")

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

# LISTAR POSTULACIONES (VISTA CANDIDATO)
@login_required
@role_required("candidato")
def listar_postulaciones(request):
    candidato = request.user.perfil_candidato
    postulaciones = Postulacion.objects.filter(candidato=candidato).select_related("oferta", "reclutador")

    estado = request.GET.get("estado")
    if estado:
        postulaciones = postulaciones.filter(estado=estado)

    return render(request, "ofertas_laborales/mis_postulaciones.html", {
        "postulaciones": postulaciones
    })        

# LISTAR POSTULACIONES (VISTA RECLUTADOR)
@login_required
def ver_postulaciones(request, id_oferta):
    oferta = get_object_or_404(OfertaLaboral, id=id_oferta, reclutador=request.user.perfil_reclutador)
    postulaciones = Postulacion.objects.filter(oferta=oferta).select_related("candidato")

    return render(request, "ofertas_laborales/ver_postulaciones.html", {
        "oferta": oferta,
        "postulaciones": postulaciones,
    })

# VER EL PERFIL DEL CANDIDATO (VISTA RECLUTADOR)
@login_required
def ver_perfil_candidato(request, id_candidato):
    # Solo los reclutadores pueden acceder
    if not hasattr(request.user, "perfil_reclutador"):
        return redirect("home")

    candidato = get_object_or_404(Candidato, id=id_candidato)

    # Buscar postulaciones del candidato (opcional, para contexto)
    postulaciones = Postulacion.objects.filter(candidato=candidato)

    return render(request, "ofertas_laborales/info_candidato.html", {
        "candidato": candidato,
        "postulaciones": postulaciones,
    })  

#AGENDAR ENTREVISTA
def agendar_entrevista(request, postulacion_id):
    postulacion = get_object_or_404(Postulacion, id_postulacion=postulacion_id)

    if request.method == "POST":
        form = EntrevistaForm(request.POST)
        if form.is_valid():
            entrevista = form.save(commit=False)
            entrevista.postulacion = postulacion
            entrevista.save()
            messages.success(request, "Entrevista agendada y correo enviado al candidato.")
            return redirect("ofertas_laborales:ver_postulaciones", postulacion.oferta.id)
    else:
        form = EntrevistaForm()

    return render(request, "ofertas_laborales/agendar_entrevista.html", {
        "form": form,
        "postulacion": postulacion,
    }) 

# DETALLE ENTREVISTA
def detalle_entrevista(request, pk):
    entrevista = get_object_or_404(Entrevista, id=pk)
    postulacion = entrevista.postulacion

    if request.method == "POST":
        form = EntrevistaForm(request.POST, instance=entrevista)
        if form.is_valid():
            form.save()  # ya actualiza el estado de la postulación automáticamente
            messages.success(request, "Entrevista actualizada correctamente.")
            return redirect("ofertas_laborales:ver_postulaciones", postulacion.oferta.id)
    else:
        form = EntrevistaForm(instance=entrevista)

    return render(request, "ofertas_laborales/detalle_entrevista.html", {
        "entrevista": entrevista,
        "form": form,
        "postulacion": postulacion,
    }) 

# PANEL DE POSTULACIONES
@login_required
def panel_postulaciones(request):
    # Obtener el reclutador logueado
    reclutador = getattr(request.user, "perfil_reclutador", None)
    if not reclutador:
        return render(request, "403.html", {"error": "Acceso no autorizado."})

    # Filtro por oferta laboral
    oferta_id = request.GET.get("oferta")

    # Obtener todas las ofertas del reclutador
    ofertas_reclutador = OfertaLaboral.objects.filter(reclutador=reclutador)

    # Filtrar postulaciones
    postulaciones = Postulacion.objects.filter(oferta__reclutador=reclutador).select_related(
        "candidato", "oferta"
    )

    if oferta_id:
        postulaciones = postulaciones.filter(oferta__id=oferta_id)

    postulaciones = postulaciones.order_by("-fecha")

    return render(request, "ofertas_laborales/panel_postulaciones.html", {
        "postulaciones": postulaciones,
        "ofertas_reclutador": ofertas_reclutador,
        "oferta_id": oferta_id,
    })    

@login_required
def panel_entrevistas(request):
    # Obtener el reclutador autenticado
    reclutador = getattr(request.user, "perfil_reclutador", None)
    if not reclutador:
        return render(request, "403.html", {"error": "Acceso no autorizado."})

    # Filtros
    filtro_fecha = request.GET.get("fecha")

    entrevistas = Entrevista.objects.filter(reclutador=reclutador).select_related(
        "candidato", "postulacion__oferta"
    )


    if filtro_fecha:
        entrevistas = entrevistas.filter(fecha=filtro_fecha)

    entrevistas = entrevistas.order_by("-fecha", "-hora")

    return render(request, "ofertas_laborales/panel_entrevistas.html", {
        "entrevistas": entrevistas,
        "filtro_fecha": filtro_fecha,
    })    

# REGISTRAR RESULTADO POSTULACION
@login_required
def cambiar_estado_postulacion(request, id_postulacion, nuevo_estado):
    postulacion = get_object_or_404(Postulacion, id_postulacion=id_postulacion)

    if postulacion.reclutador.usuario != request.user:
        messages.error(request, "No tienes permiso para modificar esta postulación.")
        return redirect("ofertas_laborales:vista_reclutador")

    postulacion.estado = nuevo_estado
    postulacion.save()

    # Enviar correo al candidato
    if postulacion.candidato and postulacion.candidato.usuario.email:
        asunto = f"Resultado de tu postulación - HireUp"
        if nuevo_estado == "aprobada":
            mensaje = (
                f"Hola {postulacion.candidato.nombre},\n\n"
                f"¡Felicitaciones! Tu postulación a la oferta '{postulacion.oferta.titulo}' ha sido **aprobada**.\n\n"
                f"Nos pondremos en contacto contigo para los próximos pasos.\n\n"
                f"Saludos,\nEquipo de Reclutamiento HireUp"
            )
        else:
            mensaje = (
                f"Hola {postulacion.candidato.nombre},\n\n"
                f"Lamentamos informarte que tu postulación a la oferta '{postulacion.oferta.titulo}' ha sido **rechazada**.\n\n"
                f"Te invitamos a seguir postulando a nuevas oportunidades.\n\n"
                f"Saludos,\nEquipo de Reclutamiento HireUp"
            )

        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [postulacion.candidato.usuario.email],
            fail_silently=True,
        )

    messages.success(request, f"Postulación marcada como {nuevo_estado}.")
    return redirect("ofertas_laborales:ver_postulaciones", id_oferta=postulacion.oferta.id)            