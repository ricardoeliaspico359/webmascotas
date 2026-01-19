from django import forms
from django.contrib.auth.models import User
from .models import Propietario, Animal, Vacuna

# 1. Formulario de Registro de Usuario (Nuevo)
class RegistroUsuarioForm(forms.ModelForm):
    # Campos extra para el modelo User
    username = forms.CharField(label="Nombre de Usuario", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. juanperez'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'}))
    confirm_password = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'}))

    class Meta:
        model = Propietario
        # Estos son los campos del perfil de propietario
        fields = ['nombre_completo', 'telefono', 'direccion', 'email']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data

# 2. Formulario de Mascota (Modificado para no pedir dueño)
class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        # Excluimos 'propietario' porque se asigna automáticamente al usuario logueado
        fields = ['codigo_nfc', 'nombre', 'especie', 'raza', 'fecha_nacimiento', 'genero', 'color']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'codigo_nfc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Número de Microchip (15 dígitos)'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'especie': forms.TextInput(attrs={'class': 'form-control'}),
            'raza': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'codigo_nfc': 'Número de Microchip / ID de Tag',
        }

# 3. Formulario de Vacunas
class VacunaForm(forms.ModelForm):
    class Meta:
        model = Vacuna
        fields = ['enfermedad', 'fecha_aplicacion', 'fecha_proxima']
        widgets = {
            'enfermedad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Rabia, Parvovirus'}),
            'fecha_aplicacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_proxima': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }