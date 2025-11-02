from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Administrador, Usuario

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_administrador(sender, instance, created, **kwargs):
    """
    Si el usuario creado es un superusuario (is_superuser=True),
    crea automáticamente su perfil de Administrador.
    """
    if created and instance.is_superuser:
        if not hasattr(instance, "perfil_admin"):
            Administrador.objects.create(
                usuario=instance,
                rut="00000000-0",
                nombre="admin",
                apellido="Administrador",
                nivel_acceso="1",
            )
