from django.core.management.base import BaseCommand
from core.models import Mascota  # Asegúrate de importar tu modelo
import serial
import time

class Command(BaseCommand):
    help = 'Escribe los datos de una mascota en una tarjeta NFC vía ESP32'

    def add_arguments(self, parser):
        parser.add_argument('mascota_id', type=int, help='ID de la mascota a grabar')
        parser.add_argument('--port', type=str, default='COM3', help='Puerto USB del ESP32 (Ej: COM3 o /dev/ttyUSB0)')

    def handle(self, **options):
        mascota_id = options['mascota_id']
        port = options['port']

        try:
            # 1. Obtener datos de la BD
            mascota = Mascota.objects.filter(id=mascota_id).first()
            if mascota is None:
                self.stdout.write(self.style.ERROR(f'No existe mascota con ID {mascota_id}'))
                return

            # Formatear datos (Máximo 16 caracteres para este ejemplo simple)
            # Ejemplo: "Rex-099123456"
            datos_a_enviar = f"{mascota.nombre}-{mascota.telefono}"[:16] 
            
            self.stdout.write(f"Conectando al ESP32 en {port}...")
            
            # 2. Abrir conexión Serial
            arduino = serial.Serial(port, 115200, timeout=2)
            time.sleep(2) # Esperar a que el ESP32 se reinicie al conectar
            
            # 3. Enviar datos
            self.stdout.write(f"Enviando datos: {datos_a_enviar}")
            arduino.write((datos_a_enviar + '\n').encode())

            # 4. Esperar confirmación del ESP32
            self.stdout.write("Acerque el llavero al lector ahora...")
            
            while True:
                if arduino.in_waiting > 0:
                    respuesta = arduino.readline().decode('utf-8').strip()
                    self.stdout.write(f"ESP32 dice: {respuesta}")
                    if "EXITO" in respuesta:
                        self.stdout.write(self.style.SUCCESS('¡Mascota grabada en el llavero exitosamente!'))
                        break
                    if "ERROR" in respuesta:
                        self.stdout.write(self.style.ERROR('Error al grabar.'))
                        break
            
            arduino.close()

        except Mascota.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No existe mascota con ID {mascota_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error de conexión: {str(e)}'))