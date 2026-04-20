# Lumina-Control

A lightweight, Python-based hardware control center for Linux, specifically designed for systems running **CachyOS** and **Hyprland** ([Caelestia](https://github.com/caelestia-dots/caelestia)).

Lumina-Control bridges the gap for Linux users by providing a centralized GUI to manage components that typically require Windows-only bloatware.

## Current Status: First Look (v0.1-alpha)
The core infrastructure is functional. The application can now communicate with NVIDIA GPUs, Motherboard sensors (NCT chips), and OpenRGB.

---

## Features

### 1. Hardware Monitoring (Dynamic)
* **Real-time Stats:** Live monitoring of CPU-Usage, CPU-Temp, RAM-Usage, and SSD-Usage.
* **GPU Insights:** Full data for NVIDIA GPUs (Usage, Temperature, VRAM).
* **RPM Tracking:** Displays actual system fan speeds in RPM alongside percentage values.

### 2. Intelligent Cooling
* **Manual Control:** Set GPU and System fan speeds via sliders (10% - 100%).
* **Quick Presets:** Instant buttons for 25%, 50%, 75%, and 100% speed.
* **Auto Fan Curve:** A smart automation mode that adjusts cooling based on the highest temperature (CPU/GPU) while preventing controller spamming.

### 3. Lighting Control
* **OpenRGB Integration:** Seamless control of connected ARGB devices, keyboards, and mice.
* **Manual Color Mixing:** Custom R/G/B sliders to create your perfect setup.
* **State Persistence:** Reads current hardware colors on startup.

---


## Roadmap
- [x] Initial GUI & Monitoring
- [x] Manual & Auto Fan Control
- [x] RGB Integration via OpenRGB
- [ ] **System Color Sync:** Automatically match hardware lighting with Hyprland/Caelestia theme colors.
- [ ] Profile Management (Save/Load settings)
- [ ] Easy installation script for Arch/CachyOS.

---

**Developed with 💙 by Jojo**