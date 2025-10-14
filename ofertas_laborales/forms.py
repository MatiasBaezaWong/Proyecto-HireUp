from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from main.models import Candidato, Usuario, OfertaLaboral

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
        """Validar el CV (tipo de archivo y tamaño máximo)"""
        cv = self.cleaned_data.get("cv", False)
        if cv:
            if cv.size > 5 * 1024 * 1024:  # 5 MB
                raise ValidationError("El archivo es demasiado grande (máximo 5 MB).")

            valid_extensions = [".pdf", ".docx"]
            if not any(cv.name.lower().endswith(ext) for ext in valid_extensions):
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
    class Meta:
        model = OfertaLaboral
        fields = [
            "titulo",
            "descripcion",
            "requisitos",
            "obra",
            "cargo",
            "tipo_contrato",
            "ubicacion",
            "salario_estimado",
            "estado",
        ]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Técnico en Ascensores"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Describe la oferta..."}),
            "requisitos": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Ej. Certificación SEC, experiencia mínima 2 años..."}),
            "obra": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Torre Costanera"}),
            "cargo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Técnico en Instalación"}),
            "tipo_contrato": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Plazo fijo o Indefinido"}),
            "ubicacion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Santiago, Chile"}),
            "salario_estimado": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej. 850000"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
        }  
