from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Autenticación (Nuevas Rutas) ---
    path('registro/', views.registrar_usuario, name='registrar_usuario'),
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),

    # --- Rutas Generales ---
    path('', views.lista_mascotas, name='lista_mascotas'),
    # Cambiamos la ruta de registro de mascota para ser más descriptivos
    path('registrar-mascota/', views.registrar_mascota, name='registrar_mascota'),
    
    # --- Rutas de Detalle y Acciones ---
    path('mascota/<int:animal_id>/', views.detalle_mascota, name='detalle_mascota'),
    path('mascota/<int:animal_id>/vacuna/', views.registrar_vacuna, name='registrar_vacuna'),
    path('mascota/<int:animal_id>/qr/', views.descargar_qr, name='descargar_qr'),
]