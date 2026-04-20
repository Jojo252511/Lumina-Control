import os
import sys

CHIP_NAME = "nct6798"
HWMON_DIR = "/sys/class/hwmon"

def find_nct_path():
    # Sucht automatisch den Ordner für den nct6798 Chip
    for hwmon in os.listdir(HWMON_DIR):
        name_path = os.path.join(HWMON_DIR, hwmon, "name")
        if os.path.exists(name_path):
            with open(name_path, 'r') as f:
                if f.read().strip() == CHIP_NAME:
                    return os.path.join(HWMON_DIR, hwmon)
    return None

def set_fan_speed(pwm_index, speed_percent):
    print("--- Lumina-Control: System Fan Control ---")
    
    base_path = find_nct_path()
    if not base_path:
        print(f"Error: Could not find {CHIP_NAME} chip in {HWMON_DIR}.")
        return

    print(f"Found {CHIP_NAME} at: {base_path}")

    # Die Ziel-Dateien zusammenbauen
    pwm_file = os.path.join(base_path, f"pwm{pwm_index}")
    enable_file = os.path.join(base_path, f"pwm{pwm_index}_enable")

    if not os.path.exists(pwm_file) or not os.path.exists(enable_file):
        print(f"Error: Control files for pwm{pwm_index} do not exist.")
        return

    # Umrechnung von 0-100% in 0-255 PWM
    speed_percent = max(0, min(100, int(speed_percent)))
    pwm_value = int((speed_percent / 100) * 255)

    try:
        # Schritt 1: Lüfter auf "Manuell" setzen (Modus 1)
        with open(enable_file, 'w') as f:
            f.write('1\n')
        
        # Schritt 2: Den neuen PWM-Wert schreiben
        with open(pwm_file, 'w') as f:
            f.write(f'{pwm_value}\n')
        
        print(f"Success: Fan pwm{pwm_index} set to {speed_percent}% (PWM value: {pwm_value})")

    except PermissionError:
        print("Error: Permission denied! Hardware access requires 'sudo'.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        pwm_idx = sys.argv[1]
        speed_pct = sys.argv[2]
        set_fan_speed(pwm_idx, speed_pct)
    else:
        print("Usage: sudo python set_sys_fan.py <pwm_index> <speed_percent>")
        print("Example: sudo python set_sys_fan.py 2 100  (Sets pwm2 to 100%)")