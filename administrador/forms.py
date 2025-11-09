import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from main.models import Usuario, Reclutador, Candidato, Comuna, Ciudad, Region, Obra

# FORMULARIO CREACION RECLUTADOR
class RegistroReclutadorForm(UserCreationForm):
    AREAS = [
        ("instalacion", "Instalación"),
        ("mantencion", "Mantención"),
        ("administracion", "Administración"),
        ("control de calidad", "Control de Calidad"),
        ("seguridad", "Seguridad"),
    ]

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "ejemplo@empresa.cl"
        })
    )
    rut = forms.CharField(
        label="RUT",
        max_length=12,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "12345678-9"
        })
    )
    nombre = forms.CharField(
        label="Nombre",
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nombre del reclutador"
        })
    )
    apellido = forms.CharField(
        label="Apellido",
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Apellido del reclutador"
        })
    )
    area = forms.ChoiceField(
        label="Área",
        choices=AREAS,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )
    telefono = forms.CharField(
        label="Teléfono de contacto",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+56 9 1234 5678"
        })
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese una contraseña segura"
        })
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Repita la contraseña"
        })
    )

    class Meta:
        model = Usuario
        fields = (
            "email", "rut", "nombre", "apellido",
            "area", "telefono", "password1", "password2"
        )

    # ------------------------
    # VALIDACIONES PERSONALIZADAS
    # ------------------------
    def clean_email(self):
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("El correo ya está registrado.")
        return email

    def clean_rut(self):
        rut = self.cleaned_data["rut"]
        if not re.match(r"^\d{7,8}-[\dkK]{1}$", rut):
            raise ValidationError("El RUT debe tener el formato 12345678-9 o 12345678-K.")
        if Reclutador.objects.filter(rut=rut).exists():
            raise ValidationError("Este RUT ya está registrado.")
        return rut

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.rol = "reclutador"
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()
            Reclutador.objects.create(
                usuario=user,
                rut=self.cleaned_data["rut"],
                nombre=self.cleaned_data["nombre"],
                apellido=self.cleaned_data["apellido"],
                area=self.cleaned_data["area"],
                telefono=self.cleaned_data["telefono"],
            )
        return user   

# FORMULARIO EDICION RECLUTADOR
class EditarReclutadorForm(forms.ModelForm):

    email = forms.EmailField(label="email", max_length=254)

    AREAS = [
        ("instalacion", "Instalacion"),
        ("mantencion", "Mantencion"),
        ("administracion", "Administracion"),
        ("control de calidad", "Control de Calidad"),
        ("seguridad", "Seguridad"),
    ]

    area = forms.ChoiceField(choices=AREAS, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Reclutador
        fields = ['rut', 'nombre', 'apellido', 'area', 'telefono', 'email']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['email'].initial = instance.usuario.email

    def save(self, commit=True):
        reclutador = super().save(commit=False)
        usuario = reclutador.usuario
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
            reclutador.save()
        return reclutador

# FORMULARIO EDICION CANDIDATO
class EditarCandidatoForm(forms.ModelForm):

    email = forms.EmailField(label="email", max_length=254)

    class Meta:
        model = Candidato
        fields = ['nombre', 'apellido', 'experiencia', 'descripcion', 'telefono', 'direccion', 'rut', 'email']
        widgets = {            
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'experiencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['email'].initial = instance.usuario.email

    def clean_rut(self):
        rut = self.cleaned_data["rut"]
        if not re.match(r"^\d{7,8}-[\dkK]{1}$", rut):
            raise ValidationError("El RUT debe tener el formato 12345678-9 o 12345678-K.")
        if Candidato.objects.filter(rut=rut).exists():
            raise ValidationError("Este RUT ya está registrado.")
        return rut        

    def save(self, commit=True):
        candidato = super().save(commit=False)
        usuario = candidato.usuario
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
            candidato.save()
        return candidato

# FORMULARIO CREACION OBRA
class ObraForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=True,
        label="Región",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    ciudad = forms.ModelChoiceField(
        queryset=Ciudad.objects.none(),
        required=True,
        label="Ciudad",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.none(),
        required=True,
        label="Comuna",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Obra
        fields = ["nombre", "descripcion", "region", "ciudad", "comuna", "direccion", "fecha_inicio", "fecha_termino"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_inicio": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fecha_termino": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "region" in self.data:
            try:
                region_id = int(self.data.get("region"))
                self.fields["ciudad"].queryset = Ciudad.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.comuna:
            self.fields["ciudad"].queryset = Ciudad.objects.filter(region=self.instance.comuna.ciudad.region)

        if "ciudad" in self.data:
            try:
                ciudad_id = int(self.data.get("ciudad"))
                self.fields["comuna"].queryset = Comuna.objects.filter(ciudad_id=ciudad_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.comuna:
            self.fields["comuna"].queryset = Comuna.objects.filter(ciudad=self.instance.comuna.ciudad)

