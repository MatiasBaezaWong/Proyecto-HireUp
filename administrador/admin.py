from django.contrib import admin
from main.models import Reclutador, Usuario, Candidato, Administrador, OfertaLaboral, Region, Ciudad, Comuna, Postulacion

# Register your models here.
admin.site.register(Reclutador)
admin.site.register(Administrador)
admin.site.register(Usuario)
admin.site.register(Candidato)
admin.site.register(OfertaLaboral)
admin.site.register(Postulacion)
admin.site.register(Region)
admin.site.register(Ciudad)
admin.site.register(Comuna)