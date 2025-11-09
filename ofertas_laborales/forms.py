import re,os
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from main.models import Candidato, Usuario, Region, Ciudad, Comuna, Obra, OfertaLaboral, Entrevista
from main.storage_utils import upload_cv

RUT_REGEX = re.compile(r'^\d{7,8}-[\dkK]$')

class EditarCandidatoForm(forms.ModelForm):
    email = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # Campo "virtual" para subir el archivo (NO está mapeado al modelo)
    cv_upload = forms.FileField(
        label="Currículum (PDF o DOCX)",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Candidato
        # OJO: NO incluir 'cv' aquí si el modelo lo tiene como URL/CharField
        fields = ['nombre', 'apellido', 'rut', 'experiencia', 'descripcion', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # bloquear RUT en edición y precargar email
            self.fields['rut'].disabled = True
            self.fields['rut'].required = False
            self.fields['rut'].widget.attrs['readonly'] = True
            if getattr(self.instance, "usuario", None):
                self.fields['email'].initial = self.instance.usuario.email

    def clean(self):
        cleaned = super().clean()
        if self.instance and self.instance.pk:
            cleaned['rut'] = self.instance.rut
        return cleaned

    def clean_rut(self):
        rut = (self.cleaned_data.get('rut') or '').strip()
        if not (self.instance and self.instance.pk):
            if not RUT_REGEX.match(rut):
                raise ValidationError("El RUT debe tener el formato 12345678-9 o 12345678-K.")
            if Candidato.objects.filter(rut=rut).exists():
                raise ValidationError("Este RUT ya está registrado.")
            return rut
        return self.instance.rut

    def validate_unique(self):
        if self.instance and self.instance.pk:
            exclusions = set(self._get_validation_exclusions())
            exclusions.add('rut')
            try:
                self.instance.validate_unique(exclude=list(exclusions))
            except ValidationError as e:
                self._update_errors(e)
        else:
            super().validate_unique()

    def save(self, commit=True):
        candidato = super().save(commit=False)

        # Blindar RUT en edición
        if self.instance and self.instance.pk:
            candidato.rut = self.instance.rut

        # Actualizar email del usuario
        usuario = getattr(candidato, "usuario", None)
        if usuario:
            usuario.email = self.cleaned_data['email']

        # Subir CV si viene
        file_obj = self.cleaned_data.get('cv_upload')
        if file_obj:
            cv_url = upload_cv(file_obj, file_obj.name)  # sube a Supabase/S3/etc.
            # Asigna la URL al campo real del modelo
            candidato.cv = cv_url  # asegúrate que Candidato.cv sea URLField/CharField

        if commit:
            if usuario:
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
