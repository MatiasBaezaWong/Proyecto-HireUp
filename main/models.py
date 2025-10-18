from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.

# =============================
# USUARIO Y ROLES
# =============================
class Usuario(AbstractUser):
    ROLES = [
        ("candidato", "Candidato"),
        ("reclutador", "Reclutador"),
        ("administrador", "Administrador"),
    ]

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES)

    first_name = None
    last_name = None

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "rol"]

    def __str__(self):
        return f"{self.username} ({self.rol})"


# =============================
# CANDIDATO
# =============================
class Candidato(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil_candidato")
    rut = models.CharField("RUT", max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    experiencia = models.PositiveIntegerField("Años de experiencia", default=0)
    descripcion = models.TextField("Descripcion", blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    cv = models.URLField("CV", max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rut})"


# =============================
# RECLUTADOR
# =============================
class Reclutador(models.Model):
    AREAS = [
        ("instalacion", "Instalacion"),
        ("mantencion", "Mantencion"),
        ("administracion", "Administracion"),
        ("control de calidad", "Control de Calidad"),
        ("seguridad", "Seguridad"),
    ]

    usuario = models.OneToOneField("Usuario", on_delete=models.CASCADE, related_name="perfil_reclutador")
    rut = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    area = models.CharField(max_length=50, choices=AREAS)

    def __str__(self):
        return f"Reclutador: {self.nombre} {self.apellido}"


# =============================
# ADMINISTRADOR
# =============================
class Administrador(models.Model):
    usuario = models.OneToOneField("Usuario", on_delete=models.CASCADE, related_name="perfil_admin")
    rut = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    nivel_acceso = models.CharField(max_length=50)

    def __str__(self):
        return f"Admin: {self.nombre} {self.apellido}"

# =============================
# OFERTA LABORAL
# =============================
class OfertaLaboral(models.Model):
    ESTADOS = [
        ("abierta", "Abierta"),
        ("cerrada", "Cerrada"),
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
    ]

    titulo = models.CharField(max_length=50)
    descripcion = models.TextField(max_length=500)
    requisitos = models.TextField(max_length=800, default="Ninguno")
    obra = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)
    tipo_contrato = models.CharField(max_length=50, default="Plazo fijo")
    ubicacion = models.CharField(max_length=255, default="No especificada")
    salario_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_publicacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50, choices=ESTADOS, default="abierta")

    reclutador = models.ForeignKey(Reclutador, on_delete=models.CASCADE, related_name="ofertas")

    def __str__(self):
        return f"{self.titulo} - {self.cargo} ({self.estado})"


# =============================
# POSTULACIÓN
# =============================
class Postulacion(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("rechazada", "Rechazada"),
        ("aprobada", "Aprobada"),
    ]

    id_postulacion = models.AutoField(primary_key=True)
    fecha = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50, choices=ESTADOS, default="pendiente")

    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name="postulaciones")
    oferta = models.ForeignKey(OfertaLaboral, on_delete=models.CASCADE, related_name="postulaciones")
    reclutador = models.ForeignKey(Reclutador, on_delete=models.CASCADE, related_name="postulaciones")

    def __str__(self):
        return f"Postulación {self.id_postulacion} - {self.estado}"


# =============================
# ENTREVISTA
# =============================
class Entrevista(models.Model):
    MODALIDAD = [
        ("online", "Online"),
        ("presencial", "Presencial"),
    ]

    RESULTADOS = [
        ("pendiente", "Pendiente"),
        ("rechazado", "Rechazado"),
        ("aprobado", "Aprobado"),
    ]

    id_entrevista = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    modalidad = models.CharField(max_length=25, choices=MODALIDAD)
    comentarios = models.TextField(max_length=225, blank=True, null=True)
    resultado = models.CharField(max_length=50, choices=RESULTADOS, default="pendiente")

    postulacion = models.ForeignKey(Postulacion, on_delete=models.CASCADE, related_name="entrevistas")
    reclutador = models.ForeignKey(Reclutador, on_delete=models.SET_NULL, null=True, blank=True)
    candidato = models.ForeignKey(Candidato, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # ✅ heredar datos automáticamente
        if self.postulacion:
            self.reclutador = self.postulacion.reclutador
            self.candidato = self.postulacion.candidato
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Entrevista {self.id_entrevista} - {self.resultado}"


