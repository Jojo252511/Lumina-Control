import pynvml
import sys

def set_fan_speed(speed_percent):
    print(f"--- Lumina-Control: Setze GPU Lüfter auf {speed_percent}% ---")
    
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        
        speed = max(0, min(100, int(speed_percent)))
        

        pynvml.nvmlDeviceSetFanSpeed_v2(handle, 0, speed) 
        
        print("Erfolg!")

    except pynvml.NVMLError_NoPermission:
        print("Fehler: Keine Berechtigung! (Liefere das Skript mit 'sudo' aus)")
    except pynvml.NVMLError_NotSupported:
        print("Fehler: Manuelle Steuerung nicht unterstützt. (Zero-RPM aktiv oder 'Coolbits' fehlen im Nvidia-Treiber)")
    except pynvml.NVMLError as error:
        print(f"NVIDIA API Fehler: {error}")
    finally:
        pynvml.nvmlShutdown()

if __name__ == "__main__":
    # Prüfen, ob ein Wert beim Start übergeben wurde
    if len(sys.argv) > 1:
        set_fan_speed(sys.argv[1])
    else:
        print("Bitte gib einen Prozentwert an. Beispiel: sudo python set_gpu_fan.py 50")