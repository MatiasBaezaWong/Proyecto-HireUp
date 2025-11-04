import re
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from main.models import Candidato, Usuario, Region, Ciudad, Comuna, Obra, OfertaLaboral, Entrevista

class EditarCandidatoForm(forms.ModelForm):
    
    email = forms.EmailField(
        label="Correo",
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    cv = forms.FileField(
        label="Currículum (PDF o DOCX)",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Candidato
        fields = ['nombre', 'apellido', 'rut', 'experiencia','descripcion', 'telefono', 'direccion', 'cv']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'experiencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cv(self):
        cv = self.cleaned_data.get("cv")

        if not cv or isinstance(cv, str):
            return cv

        if cv.size > 5 * 1024 * 1024:
            raise ValidationError("El archivo es demasiado grande (máximo 5 MB).")

        valid_extensions = [".pdf", ".docx"]
        ext = os.path.splitext(cv.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError("Solo se permiten archivos PDF o DOCX.")

        return cv

    def clean_rut(self):
        rut = self.cleaned_data["rut"]
        if not re.match(r"^\d{7,8}-[\dkK]{1}$", rut):
            raise ValidationError("El RUT debe tener el formato 12345678-9 o 12345678-K.")
        if Candidato.objects.filter(rut=rut).exists():
            raise ValidationError("Este RUT ya está registrado.")
        return rut    


    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['email'].initial = instance.usuario.email

    def save(self, commit=True):
        candidato = super().save(commit=False)
        usuario = candidato.usuario
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
            candidato.save()
        return candidato


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

#Registro Ofertas Laborales
class CrearOfertaForm(forms.ModelForm):

    obra = forms.ModelChoiceField(
        queryset=Obra.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Obra"
    )

    class Meta:
        model = OfertaLaboral
        fields = [
            "titulo",
            "descripcion",
            "requisitos",
            "experiencia_minima",
            "obra",
            "cargo",
            "tipo_contrato",
            "salario_estimado",
            "estado",
            "limite_postulaciones",
        ]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Técnico en Ascensores"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Describe la oferta..."}),
            "requisitos": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Ej. Certificación SEC, experiencia mínima 2 años..."}),
            "experiencia_minima": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej. 2 años minimo"}),
            "cargo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Técnico en Instalación"}),
            "tipo_contrato": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Plazo fijo o Indefinido"}),
            "salario_estimado": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej. 850000"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "limite_postulaciones": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Maximo de postulaciones"}),
        }   

#REGISTRO ENTREVISTA
class EntrevistaForm(forms.ModelForm):
    class Meta:
        model = Entrevista
        fields = ["fecha", "hora", "modalidad", "comentarios"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hora": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "modalidad": forms.Select(attrs={"class": "form-select"}),
            "comentarios": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }          
