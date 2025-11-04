from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
import pandas as pd
import openpyxl
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
import io
from datetime import datetime

from .forms import RegistroReclutadorForm, EditarReclutadorForm, EditarCandidatoForm, ObraForm
from main.models import Usuario, Reclutador, Candidato, Obra, OfertaLaboral, Postulacion, Entrevista

# Create your views here.

# PORTAL ADMINISTRADOR
@login_required
def portal_administrador(request):
    # Restringir acceso solo a administradores
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado")

    # Formulario de creación de reclutador
    total_usuarios = Usuario.objects.count()
    total_reclutadores = Reclutador.objects.count()
    total_candidatos = Candidato.objects.count()
    total_ofertas = OfertaLaboral.objects.count()
    total_postulaciones = Postulacion.objects.count()
    total_entrevistas = Entrevista.objects.count()

    # Listar todos los usuarios existentes
    reclutadores = Reclutador.objects.select_related("usuario").all()
    candidatos = Candidato.objects.select_related("usuario").all()
    usuarios = Usuario.objects.all().select_related()

    return render(request, "administrador/portal_administrador.html", {
        "usuarios": usuarios,
        "total_usuarios": total_usuarios,
        "total_reclutadores": total_reclutadores,
        "total_candidatos": total_candidatos,
        "total_ofertas": total_ofertas,
        "total_postulaciones": total_postulaciones,
        "total_entrevistas": total_entrevistas,
    })

@login_required
def panel_usuarios(request):
    buscar = request.GET.get("buscar", "")
    rol = request.GET.get("rol", "")
    area = request.GET.get("area", "")

    reclutadores = Reclutador.objects.select_related("usuario").all()
    candidatos = Candidato.objects.select_related("usuario").all()

    usuarios = list(reclutadores) + list(candidatos)

    # Formulario de Creacion del Reclutador
    if request.method == "POST":
        form = RegistroReclutadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reclutador creado con éxito.")
            return redirect("administrador:portal_administrador")
    else:
        form = RegistroReclutadorForm()

    # Filtrado
    if buscar:
        usuarios = [u for u in usuarios if buscar.lower() in u.usuario.email.lower() or buscar.lower() in u.nombre.lower()]
    if rol:
        usuarios = [u for u in usuarios if u.usuario.rol == rol]
    if area:
        usuarios = [u for u in usuarios if hasattr(u, "area") and u.area == area]

    # Estadísticas
    total_usuarios = Usuario.objects.count()
    total_reclutadores = Reclutador.objects.count()
    total_candidatos = Candidato.objects.count()

    areas = Reclutador.objects.values_list("area", flat=True).distinct()

    return render(request, "administrador/panel_usuarios.html", {
        "form": form,
        "usuarios": usuarios,
        "total_usuarios": total_usuarios,
        "total_reclutadores": total_reclutadores,
        "total_candidatos": total_candidatos,
        "areas": areas,
        "buscar": buscar,
        "rol": rol,
        "area_seleccionada": area,
    })

@login_required
def exportar_usuarios_excel(request):
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado")

    data = []
    usuarios = Usuario.objects.all()

    for user in usuarios:
        data.append({
            "ID": user.id,
            "Correo": user.email,
            "Rol": user.rol,
            "Fecha Registro": user.date_joined.strftime("%Y-%m-%d"),
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = f'attachment; filename="usuarios_{timezone.now().date()}.xlsx"'
    df.to_excel(response, index=False)
    return response 

@login_required
def generar_informe_pdf(request):
    if request.user.rol != "administrador":
        return HttpResponseForbidden("Acceso denegado")

    # Datos generales
    total_usuarios = Usuario.objects.count()
    total_reclutadores = Reclutador.objects.count()
    total_candidatos = Candidato.objects.count()

    # Configuración inicial PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    style_title = styles["Title"]
    style_heading = styles["Heading2"]
    style_body = styles["BodyText"]

    # Logo (opcional, si tienes uno)
    logo_path = "static/images/logo.png"
    elements.append(Image(logo_path, width=1.5*inch, height=1.5*inch))

    # Título principal
    elements.append(Paragraph("Informe General de Usuarios - HireUp", style_title))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", style_body))
    elements.append(Spacer(1, 20))

    # Sección de métricas
    elements.append(Paragraph("📊 Resumen General", style_heading))
    data_resumen = [
        ["Total de Usuarios", total_usuarios],
        ["Reclutadores Registrados", total_reclutadores],
        ["Candidatos Registrados", total_candidatos],
    ]
    table = Table(data_resumen, colWidths=[3.5 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00bfa6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Detalle de reclutadores
    elements.append(Paragraph("👔 Reclutadores Registrados", style_heading))
    reclutadores_data = [["Nombre", "Correo", "Área", "RUT"]]
    for r in Reclutador.objects.select_related("usuario"):
        reclutadores_data.append([
            f"{r.nombre} {r.apellido}",
            r.usuario.email,
            r.area.capitalize(),
            r.rut,
        ])
    table_reclutadores = Table(reclutadores_data, colWidths=[2.2*inch, 2.2*inch, 1.5*inch, 1.3*inch])
    table_reclutadores.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(table_reclutadores)
    elements.append(Spacer(1, 20))

    # Detalle de candidatos
    elements.append(Paragraph("🧑‍🔧 Candidatos Registrados", style_heading))
    candidatos_data = [["Nombre", "Correo", "Experiencia (años)", "RUT"]]
    for c in Candidato.objects.select_related("usuario"):
        candidatos_data.append([
            f"{c.nombre} {c.apellido}",
            c.usuario.email,
            c.experiencia,
            c.rut,
        ])
    table_candidatos = Table(candidatos_data, colWidths=[2.2*inch, 2.2*inch, 1.5*inch, 1.3*inch])
    table_candidatos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#28a745")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(table_candidatos)

    # Generar documento
    doc.build(elements)
    buffer.seek(0)

    # Respuesta HTTP
    return FileResponse(buffer, as_attachment=True, filename=f"informe_usuarios_{datetime.now().date()}.pdf")

# CREAR RECLUTADOR
@login_required
def crear_reclutador(request):
    if request.method == "POST":
        form = RegistroReclutadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reclutador creado con éxito.")
            return redirect("administrador:panel_usuarios")
    else:
        form = RegistroReclutadorForm()
    return render(request, "administrador/crear_reclutador.html", {
    "form": form,
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
            return redirect("administrador:panel_usuarios")
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
        return redirect("administrador:panel_usuarios")

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
            return redirect("administrador:panel_usuarios")
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
        return redirect("administrador:panel_usuarios")

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