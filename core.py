import psutil
import pynvml
import time
import platform

def get_cpu_name():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('model name'):
                    return line.split(':')[1].strip()
    except Exception:
        return platform.processor()
    return "Unknown CPU"

def read_hardware():
    print("--- Lumina-Control: System Overview ---")

    # 1. CPU & RAM Data
    cpu_name = get_cpu_name()
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    
    # Convert RAM to GB
    ram_used_gb = ram.used / (1024**3)
    ram_total_gb = ram.total / (1024**3)

    print(f"CPU Model:       {cpu_name}")
    print(f"CPU Usage:       {cpu_usage}%")
    print(f"RAM Usage:       {ram.percent}% ({ram_used_gb:.1f} GB / {ram_total_gb:.1f} GB)")

    # 2. GPU Data
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
        
        # Convert VRAM to GB
        vram_used_gb = memory.used / (1024**3)
        vram_total_gb = memory.total / (1024**3)

        print(f"GPU Model:       {gpu_name}")
        print(f"GPU Usage:       {utilization.gpu}%")
        print(f"GPU Temperature: {temperature}°C")
        print(f"VRAM Usage:      {vram_used_gb:.1f} GB / {vram_total_gb:.1f} GB")

    except pynvml.NVMLError as error:
        print(f"NVIDIA API Error: {error}")
    finally:
        pynvml.nvmlShutdown()

if __name__ == "__main__":
    read_hardware()