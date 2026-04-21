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
            print(f" -> Processing: {device.name}")
            
            # 1. Force the correct mode (Static or Direct)
            try:
                for mode in device.modes:
                    # We are looking for the standard names for static lighting
                    if mode.name.lower() in ['direct', 'static', 'custom']:
                        device.set_mode(mode)
                        time.sleep(0.1) # Give the hardware a fraction of a second to switch
                        break
            except Exception as e:
                print(f"    (Mode warning: {e})")

            # 2. Set the actual color
            try:
                device.set_color(color)
                print("    [OK] Color set.")
            except Exception as e:
                print(f"    [Error] Could not set color: {e}")

        print("\nSuccess! Disconnecting cleanly...")
        client.disconnect() # Fixes the annoying error message at the end
        
    except ConnectionRefusedError:
        print("Error: Could not connect to OpenRGB. Is the SDK server running?")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        r, g, b = sys.argv[1], sys.argv[2], sys.argv[3]
        set_all_colors(r, g, b)
    else:
        print("Usage: python set_rgb.py <R> <G> <B>")

def get_main_color():
    try:
        client = OpenRGBClient()
        if client.devices:
            # We take the color of the first device as a reference
            device = client.devices[0]
            color = device.colors[0] # Color of the first LED
            return color.red, color.green, color.blue
        return 0, 255, 255 # Fallback
    except:
        return 0, 255, 255