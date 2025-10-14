import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Usuario, Candidato

class RegistroCandidatoForm(UserCreationForm):
    # Datos de usuario
    username = forms.CharField(label="Usuario", max_length=50)
    email = forms.EmailField(label="Correo electrónico")

    # Datos de perfil candidato
    rut = forms.CharField(label="RUT", max_length=12)
    nombre = forms.CharField(label="Nombre", max_length=50)
    apellido = forms.CharField(label="Apellido", max_length=50)
    experiencia = forms.IntegerField(label="Experiencia (años)", min_value=0)
    descripcion = forms.CharField(label="Certificaciones", max_length=255)
    telefono = forms.CharField(label="Teléfono de contacto", max_length=15, required=False)
    direccion = forms.CharField(label="Dirección", max_length=100, required=False)
    cv = forms.FileField(label="Currículum (opcional)", required=False)

    class Meta:
        model = Usuario
        fields = ("username", "email", "password1", "password2")

    #Validacion de unicidad
    def clean_username(self):
        username = self.cleaned_data["username"]
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def clean_rut(self):
        rut = self.cleaned_data["rut"]
        if not re.match(r"^\d{7,8}-[\dkK]{1}$", rut):
            raise ValidationError("El RUT debe tener el formato 12345678-9 o 12345678-K.")
        if Candidato.objects.filter(rut=rut).exists():
            raise ValidationError("Este RUT ya está registrado.")
        return rut

    def save(self, commit=True):
        # Crear usuario con rol 'candidato'
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.rol = "candidato"

        if commit:
            user.save()
            # Crear perfil candidato asociado
            Candidato.objects.create(
                usuario=user,
                rut=self.cleaned_data["rut"],
                nombre=self.cleaned_data["nombre"],
                apellido=self.cleaned_data["apellido"],
                experiencia=self.cleaned_data["experiencia"],
                descripcion=self.cleaned_data["descripcion"],
                telefono=self.cleaned_data.get("telefono"),
                direccion=self.cleaned_data.get("direccion"),
                cv=self.cleaned_data.get("cv"),
            )
        return user


class LoginUsuarioForm(AuthenticationForm):
    username = forms.CharField(label="Nombre de Usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
