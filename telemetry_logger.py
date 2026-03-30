import csv
import os
from datetime import datetime

class HardwareLogger:
    def __init__(self, filename="gpu_telemetry_log.csv"):
        self.filename = filename
        self.headers = ["Timestamp", "GPC_Util_%", "MC_Util_%", "VRAM_Used_MB", "Core_Clock_MHz", "Temp_C", "Throttle"]
        self._initialize_file()

    def _initialize_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)

    def log_snapshot(self, metrics):
        if "error" in metrics:
            return
            
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%H:%M:%S"),
                metrics["gpc_utilization"],
                metrics["mc_utilization"],
                metrics["vram_used_mb"],
                metrics["core_clock_mhz"],
                metrics["temperature_c"],
                metrics["throttle_status"]
            ])