from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Animal, Propietario, Vacuna
from .forms import AnimalForm, VacunaForm, RegistroUsuarioForm
from django.http import HttpResponse
import qrcode
from io import BytesIO

# --- SECCIÓN DE AUTENTICACIÓN ---

def registrar_usuario(request):
    """
    Vista para registrar un nuevo usuario y su perfil de propietario asociado.
    Inicia sesión automáticamente tras el registro.
    """
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # 1. Crear el Usuario de Django (Sistema de Auth)
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email']
            )
            # 2. Crear el perfil de Propietario vinculado
            propietario = form.save(commit=False)
            propietario.usuario = user
            propietario.save()
            
            # 3. Iniciar sesión automáticamente
            login(request, user)
            return redirect('lista_mascotas')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro_usuario.html', {'form': form})

def iniciar_sesion(request):
    """Vista de Login estándar"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('lista_mascotas')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def cerrar_sesion(request):
    """Cierra la sesión y redirige al login"""
    logout(request)
    return redirect('iniciar_sesion')

# --- LÓGICA DE MASCOTAS ---
def detalle_mascota(request, animal_id):
    """
    Muestra la ficha técnica. Calcula si el visitante es el dueño.
    """
    mascota = get_object_or_404(Animal, id=animal_id)
    vacunas = mascota.vacunas.all()
    
    # Lógica para determinar si el usuario actual es el dueño
    es_dueno = False
    
    # 1. ¿Está logueado?
    if request.user.is_authenticated:
        # 2. ¿Tiene perfil de propietario? (Evita error* si es SuperUser)
        if hasattr(request.user, 'propietario'):
            # 3. ¿El dueño de la mascota es ESTE usuario?
            if mascota.propietario == request.user.propietario:
                es_dueno = True

    return render(request, 'detalle_mascota.html', {
        'mascota': mascota, 
        'vacunas': vacunas, 
        'es_dueno': es_dueno # Pasamos esta variable al HTML
    })

def lista_mascotas(request):
    """
    Muestra todas las mascotas.
    Permite buscar por nombre o código de chip.
    """
    query = request.GET.get('q')
    if query:
        mascotas = Animal.objects.filter(nombre__icontains=query) | Animal.objects.filter(codigo_nfc__icontains=query)
    else:
        mascotas = Animal.objects.all()
    return render(request, 'lista_mascotas.html', {'mascotas': mascotas})

@login_required
def registrar_mascota(request):
    """
    Registra una mascota asignándola automáticamente al usuario logueado.
    """
    if request.method == 'POST':
        form = AnimalForm(request.POST)
        if form.is_valid():
            mascota = form.save(commit=False)
            # ASIGNACIÓN AUTOMÁTICA DEL DUEÑO (El usuario logueado)
            # Esto asume que el usuario tiene un perfil de propietario creado
            mascota.propietario = request.user.propietario
            mascota.save()
            return redirect('detalle_mascota', animal_id=mascota.id)
    else:
        form = AnimalForm()
    return render(request, 'form_mascota.html', {'form': form})

def detalle_mascota(request, animal_id):
    """
    Muestra la ficha técnica de la mascota.
    Verifica si el usuario actual es el dueño para mostrar opciones de edición.
    """
    mascota = get_object_or_404(Animal, id=animal_id)
    vacunas = mascota.vacunas.all()
    
    # Verificar si el usuario que ve la página es el dueño
    es_dueno = False
    if request.user.is_authenticated:
        try:
            # Comparamos el propietario de la mascota con el del usuario actual
            if mascota.propietario == request.user.propietario:
                es_dueno = True
        except Propietario.DoesNotExist:
            # Si es un admin o superusuario sin perfil de propietario
            pass

    return render(request, 'detalle_mascota.html', {
        'mascota': mascota, 
        'vacunas': vacunas, 
        'es_dueno': es_dueno
    })

@login_required
def registrar_vacuna(request, animal_id):
    """
    Agrega una vacuna al historial.
    Protegido: Solo el dueño puede acceder.
    """
    mascota = get_object_or_404(Animal, id=animal_id)
    
    # SEGURIDAD: Solo el dueño puede agregar vacunas
    if mascota.propietario != request.user.propietario:
        return redirect('detalle_mascota', animal_id=mascota.id)

    if request.method == 'POST':
        form = VacunaForm(request.POST)
        if form.is_valid():
            vacuna = form.save(commit=False)
            vacuna.animal = mascota
            vacuna.save()
            return redirect('detalle_mascota', animal_id=mascota.id)
    else:
        form = VacunaForm()
    return render(request, 'form_vacuna.html', {'form': form, 'mascota': mascota})

def descargar_qr(request, animal_id):
    """
    Genera un código QR descargable con toda la información de la mascota.
    """
    mascota = get_object_or_404(Animal, id=animal_id)
    
    # Datos extendidos para el QR (Restaurado completo)
    data = (
        f"ID Chip: {mascota.codigo_nfc}\n"
        f"Nombre: {mascota.nombre}\n"
        f"Especie: {mascota.especie}\n"
        f"Raza: {mascota.raza}\n"
        f"Genero: {mascota.genero}\n"
        f"Color: {mascota.color}\n"
        f"Nacimiento: {mascota.fecha_nacimiento}\n"
        f"Propietario: {mascota.propietario.nombre_completo}\n"
        f"Tel: {mascota.propietario.telefono}"
    )
    
    qr = qrcode.QRCode(box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="qr_{mascota.nombre}.png"'
    return response
