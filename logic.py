import time
import set_gpu_fan
import set_sys_fan
import set_rgb

class LuminaLogic:
    def __init__(self):
        self.auto_mode = False
        self.temp_limit = 75  # Ab hier wird's kritisch (Rot)

    def process_automation(self, cpu_temp, gpu_temp):
        if not self.auto_mode:
            return

        # Einfache Lüfterkurve für die GPU
        if gpu_temp < 45:
            set_gpu_fan.set_fan_speed(0) # Zero-RPM
        elif gpu_temp < 65:
            set_gpu_fan.set_fan_speed(45)
        else:
            set_gpu_fan.set_fan_speed(80)

        # RGB-Warnung: Wenn zu heiß, färbe alles Rot
        if gpu_temp > self.temp_limit or cpu_temp > self.temp_limit:
            set_rgb.set_all_colors(255, 0, 0) # Alarm-Rot
        else:
            # Hier könnten wir später den System-Color-Sync einbauen
            pass