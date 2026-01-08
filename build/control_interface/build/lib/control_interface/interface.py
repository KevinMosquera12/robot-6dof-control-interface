import serial
import serial.tools.list_ports
import time

class RobotArmController:
    def __init__(self, baudrate=9600):
        port = self.detectar_puerto_arduino()
        if port is None:
            print("No se detectó ningún puerto Arduino.")
            self.arduino = None
            return

        try:
            self.arduino = serial.Serial(port, baudrate, timeout=1)
            print(f"Conectado al puerto {port}")
        except Exception as e:
            print(f"No se pudo conectar al Arduino: {e}")
            self.arduino = None

        self.last_angles = {}

        self.min_safe_angle = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
        }

        self.servo_offsets = {
            0: 0,
            1: 0,  
            2: 0,
            3: 0,
            4: 30,
            5: 0,
        }

    def detectar_puerto_arduino(self):
        puertos = serial.tools.list_ports.comports()
        for puerto in puertos:
            if 'Arduino' in puerto.description or 'ttyUSB' in puerto.device or 'ttyACM' in puerto.device:
                return puerto.device
        return None

    def move_servo(self, servo_id: int, angle: int):
        if self.arduino is None:
            print("Arduino no conectado.")
            return

        if 0 <= servo_id <= 5 and 0 <= angle <= 180:
            offset = self.servo_offsets.get(servo_id, 0)
            real_angle = offset + angle

            real_angle = min(max(real_angle, 0), 180)
            min_angle = self.min_safe_angle.get(servo_id, 0)
            real_angle = max(real_angle, min_angle)

            if self.last_angles.get(servo_id) == real_angle:
                return

            self.last_angles[servo_id] = real_angle

            try:
                self.arduino.write(bytes([servo_id, real_angle]))
                time.sleep(0.01)
                print(f"Servo {servo_id} → Slider: {angle}°, Enviado: {real_angle}°")
            except Exception as e:
                print(f"Error al enviar datos: {e}")
        else:
            print("ID o ángulo fuera de rango.")