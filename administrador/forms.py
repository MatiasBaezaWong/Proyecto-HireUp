import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from main.models import Usuario, Reclutador, Candidato, Comuna, Obra

class RegistroReclutadorForm(UserCreationForm):
    AREAS = [
        ("instalacion", "Instalacion"),
        ("mantencion", "Mantencion"),
        ("administracion", "Administracion"),
        ("control de calidad", "Control de Calidad"),
        ("seguridad", "Seguridad"),
    ]
    email = forms.EmailField(label="Correo")
    rut = forms.CharField(label="RUT", max_length=12)
    nombre = forms.CharField(label="Nombre", max_length=50)
    apellido = forms.CharField(label="Apellido", max_length=50)
    area = forms.ChoiceField(label="Área", choices=AREAS)
    telefono = forms.CharField(label="Telefono de contacto", max_length=15, required=False)

    class Meta:
        model = Usuario
        fields = ("email", "password1", "password2")

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

    def clean_username(self):
        username = self.cleaned_data["username"]
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya está en uso. Elige otro.")
        return username

    # Validación de email
    def clean_email(self):
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("El correo ya está registrado.")
        return email

    # Validación de RUT
    def clean_rut(self):
        rut = self.cleaned_data["rut"]
        # Formato simple: 12345678-9 o 12345678-K
        if not re.match(r"^\d{7,8}-[\dkK]{1}$", rut):
            raise ValidationError("El RUT debe tener el formato 12345678-9 o 12345678-K.")

        # Validación de unicidad
        if Reclutador.objects.filter(rut=rut).exists():
            raise ValidationError("Este RUT ya está registrado.")
          
        return rut

    def save(self, commit=True):
        # crear usuario con rol 'reclutador'
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.rol = "reclutador"
        if commit:
            user.save()
            # crear perfil reclutador
            Reclutador.objects.create(
                usuario=user,
                rut=self.cleaned_data["rut"],
                nombre=self.cleaned_data["nombre"],
                apellido=self.cleaned_data["apellido"],
                area=self.cleaned_data["area"],
                telefono=self.cleaned_data["telefono"],
            )
        return user    

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

class ObraForm(forms.ModelForm):
    comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Comuna"
    )

    class Meta:
        model = Obra
        fields = ["nombre", "descripcion", "comuna", "fecha_inicio", "fecha_termino"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Torre Costanera"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fecha_termino": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }    
