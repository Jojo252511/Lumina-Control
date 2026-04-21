import time
import json
import socket
import threading
import psutil
import pynvml
import subprocess
from set_gpu_fan import set_fan_speed as set_gpu 

class LuminaDaemon:
    def __init__(self):
        self.running = True
        self.stats = {"cpu_temp": 0, "gpu_temp": 0, "sys_fan": 0, "gpu_fan": 0}
        try:
            pynvml.nvmlInit()
            self.nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        except:
            self.nvml_handle = None

        # Socket for commands from the shell
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if os.path.exists("/tmp/lumina.sock"):
            os.remove("/tmp/lumina.sock")
        self.server.bind("/tmp/lumina.sock")
        os.chmod("/tmp/lumina.sock", 0o666) # Allow shell to write

    def update_stats(self):
        while self.running:
            # CPU Temp
            temps = psutil.sensors_temperatures()
            for key in ['k10temp', 'coretemp', 'cpu_thermal', 'nct6798']:
                if key in temps and temps[key]:
                    self.stats["cpu_temp"] = int(temps[key][0].current)
                    break
            
            # Read System Fans (RPM)
            sys_rpm = 0
            fans = psutil.sensors_fans()
            if fans:
                for key in fans:
                    if fans[key]:
                        sys_rpm = max(sys_rpm, max([f.current for f in fans[key]]))
            self.stats["sys_fan"] = sys_rpm
            
            # GPU Temp
            if self.nvml_handle:
                try:
                    self.stats["gpu_temp"] = pynvml.nvmlDeviceGetTemperature(self.nvml_handle, 0)
                    self.stats["gpu_fan"] = pynvml.nvmlDeviceGetFanSpeed(self.nvml_handle)
                except Exception as e:
                    print(f"Error fetching NVML stats: {e}")

            # --- THE FILE-BASED FIX ---
            try:
                with open("/tmp/lumina_stats.json", "w") as f:
                    json.dump(self.stats, f)
                
                # Make file readable for everyone (chmod 644)
                os.chmod("/tmp/lumina_stats.json", 0o644) 
            except Exception as e:
                print(f"Error writing stats file: {e}")

            time.sleep(2)

    def listen_commands(self):
        self.server.listen(1)
        while self.running:
            conn, _ = self.server.accept()
            try:
                data = conn.recv(1024).decode()
                if data:
                    cmd = json.loads(data)
                    print(f"Command received: {cmd}")
                    if cmd["type"] == "get_stats":
                        print("--- Command received: get_stats ---")
                        conn.send(json.dumps(self.stats).encode())
                        print(json.dumps(self.stats).encode())
                    elif cmd["type"] == "set_gpu":
                        print("--- Command received: set_gpu ---")
                        set_gpu(cmd["value"])
                        conn.send(b"OK: GPU fan set.")
                    elif cmd["type"] == "start_openrgb":
                        print("--- Command received: start_openrgb ---")
                        env = os.environ.copy()
                        env["XDG_RUNTIME_DIR"] = "/run/user/1000"
                        env["WAYLAND_DISPLAY"] = "wayland-1" # On CachyOS usually wayland-1 or wayland-0
                        print(f"Environment prepared: WAYLAND_DISPLAY={env['WAYLAND_DISPLAY']}, XDG_RUNTIME_DIR={env['XDG_RUNTIME_DIR']}")
                        
                        # -E is extremely important so that sudo keeps the Wayland variables!
                        print("Opening log file /tmp/lumina_openrgb.log...")
                        log_file = open("/tmp/lumina_openrgb.log", "w")
                        print("Executing subprocess: sudo -E -u joern openrgb")
                        subprocess.Popen(
                            ["sudo", "-E", "-u", "joern", "openrgb"], 
                            env=env, 
                            start_new_session=True,
                            stdout=log_file,
                            stderr=subprocess.STDOUT
                        )
                        print("Subprocess for OpenRGB has been dispatched successfully.")
                        conn.send(b"OK: OpenRGB start command issued.")
                    elif cmd["type"] == "test":
                        print("--- Command received: test ---")
                        conn.send("Hello from Lumina-Control!".encode())
            except Exception as e:
                print(f"Error in socket communication: {e}")
            finally:
                conn.close()

if __name__ == "__main__":
    import os
    daemon = LuminaDaemon()
    threading.Thread(target=daemon.update_stats, daemon=True).start()
    daemon.listen_commands()