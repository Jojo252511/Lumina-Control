import psutil
import pynvml

def read_fans():
    print("--- Lumina-Control: Fan & Pump Check ---")

    # 1. Motherboard / System Fans
    print("\n[System Fans]")
    fans = psutil.sensors_fans()
    
    if not fans:
        print("No system fans found. (Missing kernel modules for the motherboard?)")
    else:
        for name, entries in fans.items():
            for entry in entries:
                label = entry.label if entry.label else name
                print(f"{label}: {entry.current} RPM")

    # 2. GPU Fan
    print("\n[GPU Fan]")
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        
        fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
        print(f"GPU Fan Speed: {fan_speed}%")
        
    except pynvml.NVMLError_NotSupported:
        print("Fan speed is currently not reported (Zero-RPM mode active?).")
    except pynvml.NVMLError as error:
        print(f"NVIDIA API Error: {error}")
    finally:
        pynvml.nvmlShutdown()

if __name__ == "__main__":
    read_fans()