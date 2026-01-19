from django.db import models
from django.contrib.auth.models import User # Importamos el usuario de Django

# Tabla Propietarios (Ahora vinculada al Usuario)
class Propietario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='propietario')
    nombre_completo = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    email = models.EmailField(max_length=100) # Opcional, ya que User tiene email

    def __str__(self):
        return self.nombre_completo

# Tabla Animales
class Animal(models.Model):
    GENERO_CHOICES = [
        ('Macho', 'Macho'),
        ('Hembra', 'Hembra'),
    ]
    
    codigo_nfc = models.CharField(max_length=50, unique=True, verbose_name="Número de Microchip / ID de Tag")
    nombre = models.CharField(max_length=50)
    especie = models.CharField(max_length=30)
    raza = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES)
    color = models.CharField(max_length=50)
    
    # Relación con Propietario
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='mascotas')

    def __str__(self):
        return f"{self.nombre} ({self.codigo_nfc})"

# Tabla Vacunas (Sin cambios)
class Vacuna(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='vacunas')
    enfermedad = models.CharField(max_length=50)
    fecha_aplicacion = models.DateField()
    fecha_proxima = models.DateField()

    def __str__(self):
        return f"{self.enfermedad} - {self.animal.nombre}"