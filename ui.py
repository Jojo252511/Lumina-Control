import customtkinter as ctk
import psutil
import pynvml
import os
import platform
import set_gpu_fan
import set_sys_fan
import set_rgb

# Global Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LuminaUI(ctk.CTk):
    def __init__(self):
        super().__init__(className="Lumina-Control")
        
        # Hardware Initialization
        self.cpu_name = self.get_cpu_name()
        try:
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self.gpu_name = pynvml.nvmlDeviceGetName(handle)
            self.nvml_active = True
        except:
            self.gpu_name = "NVIDIA GeForce RTX 5060"
            self.nvml_active = False

        # State tracking to prevent controller spamming
        self.last_fan_speed = None

        # Window Geometry
        window_width = 520
        window_height = 950
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.title("Lumina Control Center")

        self.auto_mode = ctk.BooleanVar(value=False)

        # --- MONITORING SECTION ---
        self.mon_frame = ctk.CTkFrame(self, corner_radius=15)
        self.mon_frame.pack(pady=15, padx=20, fill="x")
        ctk.CTkLabel(self.mon_frame, text="System Stats", font=("Arial", 20, "bold")).pack(pady=10)
        
        # CPU Info
        self.cpu_info_label = ctk.CTkLabel(self.mon_frame, text=f"CPU: {self.cpu_name}", font=("Arial", 12))
        self.cpu_info_label.pack()
        self.cpu_usage_label = ctk.CTkLabel(self.mon_frame, text="CPU-Usage: --%", font=("Arial", 12))
        self.cpu_usage_label.pack()
        self.cpu_temp_label = ctk.CTkLabel(self.mon_frame, text="CPU-Temp: --°C", font=("Arial", 12))
        self.cpu_temp_label.pack(pady=(0, 10))

        # RAM Info
        self.ram_usage_label = ctk.CTkLabel(self.mon_frame, text="RAM-Usage: --%", font=("Arial", 12))
        self.ram_usage_label.pack(pady=(0, 10))

        # GPU Info
        self.gpu_info_label = ctk.CTkLabel(self.mon_frame, text=f"GPU: {self.gpu_name}", font=("Arial", 12))
        self.gpu_info_label.pack()
        self.gpu_usage_label = ctk.CTkLabel(self.mon_frame, text="GPU-Usage: --%", font=("Arial", 12))
        self.gpu_usage_label.pack()
        self.gpu_temp_label = ctk.CTkLabel(self.mon_frame, text="GPU-Temp: --°C", font=("Arial", 12))
        self.gpu_temp_label.pack(pady=(0, 10))

        # Fan Stats
        self.fan_speed_label = ctk.CTkLabel(self.mon_frame, text="Fan-Speed: --% (-- RPM)", font=("Arial", 12))
        self.fan_speed_label.pack()
        self.gpu_fan_label = ctk.CTkLabel(self.mon_frame, text="GPU-Fan-Speed: --%", font=("Arial", 12))
        self.gpu_fan_label.pack(pady=(0, 10))

        # --- COOLING CONTROL ---
        self.fan_frame = ctk.CTkFrame(self, corner_radius=15)
        self.fan_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.fan_frame, text="Cooling Control", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.auto_switch = ctk.CTkSwitch(self.fan_frame, text="Auto Fan Curve", variable=self.auto_mode, command=self.toggle_auto)
        self.auto_switch.pack(pady=5)
        
        self.gpu_slider = ctk.CTkSlider(self.fan_frame, from_=10, to=100, command=self.manual_fan)
        self.gpu_slider.set(50)
        self.gpu_slider.pack(pady=10, padx=30, fill="x")
        
        self.btn_frame = ctk.CTkFrame(self.fan_frame, fg_color="transparent")
        self.btn_frame.pack(pady=10, padx=10, fill="x")
        
        for p in [25, 50, 75, 100]:
            ctk.CTkButton(self.btn_frame, text=f"{p}%", width=60, 
                          command=lambda val=p: self.set_fan_preset(val)).pack(side="left", padx=10, expand=True)

        # --- LIGHTING CONTROL ---
        self.rgb_frame = ctk.CTkFrame(self, corner_radius=15)
        self.rgb_frame.pack(pady=15, padx=20, fill="x")
        ctk.CTkLabel(self.rgb_frame, text="Lighting Control", font=("Arial", 18, "bold")).pack(pady=10)
        
        r_s, g_s, b_s = set_rgb.get_main_color()
        self.r_val, self.g_val, self.b_val = ctk.IntVar(value=r_s), ctk.IntVar(value=g_s), ctk.IntVar(value=b_s)
        self.create_rgb_slider("Red", self.r_val, "#FF4444")
        self.create_rgb_slider("Green", self.g_val, "#44FF44")
        self.create_rgb_slider("Blue", self.b_val, "#4444FF")
        ctk.CTkButton(self.rgb_frame, text="Apply Color", command=self.apply_custom_rgb).pack(pady=15)

        self.update_loop()

    def get_cpu_name(self):
        if platform.system() == "Linux":
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            return line.split(':')[1].strip()
            except: pass
        return platform.processor()

    def get_cpu_temp(self):
        try:
            temps = psutil.sensors_temperatures()
            for key in ['k10temp', 'nct6798', 'cpu_thermal']:
                if key in temps:
                    return int(temps[key][0].current)
        except: pass
        return 0

    def toggle_auto(self):
        # Reset last speed when toggling to ensure immediate reaction
        self.last_fan_speed = None
        self.gpu_slider.configure(state="disabled" if self.auto_mode.get() else "normal")

    def manual_fan(self, val):
        if not self.auto_mode.get():
            speed = int(val)
            if speed != self.last_fan_speed:
                set_gpu_fan.set_fan_speed(speed)
                self.last_fan_speed = speed

    def set_fan_preset(self, val):
        if self.auto_mode.get():
            self.auto_mode.set(False)
            self.toggle_auto()
        self.gpu_slider.set(val)
        self.manual_fan(val)

    def apply_custom_rgb(self):
        set_rgb.set_all_colors(self.r_val.get(), self.g_val.get(), self.b_val.get())

    def update_loop(self):
        # 1. CPU & RAM
        cpu_u = psutil.cpu_percent()
        cpu_t = self.get_cpu_temp()
        ram = psutil.virtual_memory().percent
        
        self.cpu_usage_label.configure(text=f"CPU-Usage: {cpu_u}%")
        self.cpu_temp_label.configure(text=f"CPU-Temp: {cpu_t}°C")
        self.ram_usage_label.configure(text=f"RAM-Usage: {ram}%")
        
        # 2. System Fans (RPM)
        sys_rpm = 0
        fans = psutil.sensors_fans()
        if fans:
            for key in fans:
                sys_rpm = max(sys_rpm, max([f.current for f in fans[key]]))
        
        # 3. GPU Data
        if self.nvml_active:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            try:
                gpu_fan = pynvml.nvmlDeviceGetFanSpeed(handle)
            except:
                gpu_fan = 0
            
            self.gpu_usage_label.configure(text=f"GPU-Usage: {util}%")
            self.gpu_temp_label.configure(text=f"GPU-Temp: {temp}°C")
            self.gpu_fan_label.configure(text=f"GPU-Fan-Speed: {gpu_fan}%")

            # 4. Optimized Auto Mode
            current_display_speed = int(self.gpu_slider.get())
            if self.auto_mode.get():
                ref_t = max(cpu_t, temp)
                auto_speed = 30 if ref_t < 50 else (60 if ref_t < 72 else 90)
                
                # Only call hardware if speed changed
                if auto_speed != self.last_fan_speed:
                    set_gpu_fan.set_fan_speed(auto_speed)
                    self.last_fan_speed = auto_speed
                
                self.gpu_slider.set(auto_speed)
                current_display_speed = auto_speed
            
            self.fan_speed_label.configure(text=f"Fan-Speed: {current_display_speed}% ({sys_rpm} RPM)")

        # 10s Interval
        self.after(2000, self.update_loop)

    def create_rgb_slider(self, label, var, color):
        lbl = ctk.CTkLabel(self.rgb_frame, text=f"{label}: {var.get()}")
        lbl.pack()
        ctk.CTkSlider(self.rgb_frame, from_=0, to=255, variable=var, button_color=color,
                      command=lambda v, l=lbl, n=label: l.configure(text=f"{n}: {int(v)}")).pack(fill="x", padx=30)

if __name__ == "__main__":
    app = LuminaUI()
    app.mainloop()