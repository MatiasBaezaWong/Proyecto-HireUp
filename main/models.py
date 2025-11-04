from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail

# Create your models here.

# =============================
# GESTOR PERSONALIZADO
# =============================
class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("El correo electrónico es obligatorio"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("rol", "administrador")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("El superusuario debe tener is_staff=True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("El superusuario debe tener is_superuser=True"))

        return self.create_user(email, password, **extra_fields)

# =============================
# USUARIO BASE
# =============================
class Usuario(AbstractUser):
    ROLES = [
        ("candidato", "Candidato"),
        ("reclutador", "Reclutador"),
        ("administrador", "Administrador"),
    ]

    username = None
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    first_name = None
    last_name = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["rol"]

    def __str__(self):
        return f"{self.username} ({self.rol})"


# =============================
# CANDIDATO
# =============================
class Candidato(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil_candidato")
    rut = models.CharField("RUT", max_length=12, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    experiencia = models.PositiveIntegerField("Años de experiencia", default=0)
    descripcion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    cv = models.URLField("CV", null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rut})"


# =============================
# RECLUTADOR
# =============================
class Reclutador(models.Model):
    AREAS = [
        ("instalacion", "Instalación"),
        ("mantencion", "Mantención"),
        ("administracion", "Administración"),
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
# UBICACIÓN
# =============================
class Region(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="ciudades")

    class Meta:
        unique_together = ('nombre', 'region')

    def __str__(self):
        return f"{self.nombre}, {self.region.nombre}"


class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name="comunas")

    class Meta:
        unique_together = ('nombre', 'ciudad')

    def __str__(self):
        return f"{self.nombre}, {self.ciudad.nombre}"

# =============================
# OBRA
# =============================
class Obra(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    comuna = models.ForeignKey("Comuna", on_delete=models.SET_NULL, null=True, related_name="obras")
    ubicacion = models.CharField(max_length=255, blank=True, editable=False)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_termino = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Generar automáticamente la ubicación
        if self.comuna:
            ciudad = self.comuna.ciudad.nombre
            region = self.comuna.ciudad.region.nombre
            self.ubicacion = f"{self.comuna.nombre}, {ciudad}, {region}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre



# =============================
# OFERTA LABORAL
# =============================
class OfertaLaboral(models.Model):
    ESTADOS = [
        ("abierta", "Abierta"),
        ("cerrada", "Cerrada"),
    ]

    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    requisitos = models.TextField(max_length=800, default="Ninguno")
    cargo = models.CharField(max_length=100)
    tipo_contrato = models.CharField(max_length=50, default="Plazo fijo")
    salario_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_publicacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50, choices=ESTADOS, default="abierta")
    experiencia_minima = models.PositiveIntegerField(default=0)
    limite_postulaciones = models.PositiveIntegerField(default=0)
    area = models.CharField(max_length=50, blank=True, null=True)
    obra = models.ForeignKey("Obra", on_delete=models.CASCADE, related_name="ofertas")

    reclutador = models.ForeignKey(Reclutador, on_delete=models.CASCADE, related_name="ofertas")

    def save(self, *args, **kwargs):

        if not self.area and self.reclutador:
            self.area = self.reclutador.area
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):

        if self.oferta.estado != "abierta":
            raise ValueError("La oferta ya está cerrada y no acepta más postulaciones.")

        total_postulaciones = Postulacion.objects.filter(oferta=self.oferta).count()

        if self.candidato.experiencia < self.oferta.experiencia_minima:
            raise ValueError(
                f"Tu experiencia ({self.candidato.experiencia} años) no cumple con la mínima requerida ({self.oferta.experiencia_minima} años)."
            )

        if self.oferta.limite_postulaciones and total_postulaciones >= self.oferta.limite_postulaciones:
            self.oferta.estado = "cerrada"
            self.oferta.save()
            raise ValueError("Se ha alcanzado el límite máximo de postulaciones para esta oferta.")

        super().save(*args, **kwargs)

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

    fecha = models.DateField()
    hora = models.TimeField()
    modalidad = models.CharField(max_length=25, choices=MODALIDAD)
    comentarios = models.TextField(max_length=225, blank=True, null=True)

    postulacion = models.ForeignKey("Postulacion", on_delete=models.CASCADE, related_name="entrevistas")
    reclutador = models.ForeignKey("Reclutador", on_delete=models.SET_NULL, null=True, blank=True)
    candidato = models.ForeignKey("Candidato", on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.postulacion:
            self.reclutador = self.postulacion.reclutador
            self.candidato = self.postulacion.candidato

        super().save(*args, **kwargs)
        self.enviar_correo_confirmacion()

    def enviar_correo_confirmacion(self):
        """Envía correo con los datos de la entrevista al candidato"""
        if not self.candidato or not self.candidato.usuario.email:
            return

        asunto = f"Detalles de tu entrevista - HireUp"
        mensaje = (
            f"Hola {self.candidato.nombre},\n\n"
            f"Has sido citado a una entrevista para tu postulación.\n\n"
            f"📅 Fecha: {self.fecha.strftime('%d/%m/%Y')}\n"
            f"🕒 Hora: {self.hora.strftime('%H:%M')}\n"
            f"💻 Modalidad: {self.modalidad.capitalize()}\n"
            f"📍 Comentarios: {self.comentarios or 'Sin comentarios adicionales'}\n\n"
            f"Saludos,\nEquipo de Reclutamiento HireUp"
        )

        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [self.candidato.usuario.email],
            fail_silently=True,
        )

    def __str__(self):
        return f"Entrevista {self.id} - {self.modalidad.capitalize()}"



