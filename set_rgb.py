from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import sys
import time

def set_all_colors(r, g, b):
    print(f"--- Lumina-Control: RGB Sync ({r}, {g}, {b}) ---")
    
    try:
        client = OpenRGBClient()
        devices = client.devices
        color = RGBColor(int(r), int(g), int(b))
        
        for device in devices:
            print(f" -> Bearbeite: {device.name}")
            
            # 1. Den richtigen Modus erzwingen (Static oder Direct)
            try:
                for mode in device.modes:
                    # Wir suchen nach den Standard-Namen für statische Beleuchtung
                    if mode.name.lower() in ['direct', 'static', 'custom']:
                        device.set_mode(mode)
                        time.sleep(0.1) # Der Hardware einen Bruchteil einer Sekunde zum Umschalten geben
                        break
            except Exception as e:
                print(f"    (Modus-Warnung: {e})")

            # 2. Die eigentliche Farbe setzen
            try:
                device.set_color(color)
                print("    [OK] Farbe gesetzt.")
            except Exception as e:
                print(f"    [Fehler] Konnte Farbe nicht setzen: {e}")

        print("\nErfolg! Verbindung wird sauber getrennt...")
        client.disconnect() # Behebt die nervige Fehlermeldung am Ende
        
    except ConnectionRefusedError:
        print("Fehler: Konnte nicht zu OpenRGB verbinden. Läuft der SDK Server?")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        r, g, b = sys.argv[1], sys.argv[2], sys.argv[3]
        set_all_colors(r, g, b)
    else:
        print("Nutzung: python set_rgb.py <R> <G> <B>")

def get_main_color():
    try:
        client = OpenRGBClient()
        if client.devices:
            # Wir nehmen die Farbe des ersten Geräts als Referenz
            device = client.devices[0]
            color = device.colors[0] # Farbe der ersten LED
            return color.red, color.green, color.blue
        return 0, 255, 255 # Fallback
    except:
        return 0, 255, 255