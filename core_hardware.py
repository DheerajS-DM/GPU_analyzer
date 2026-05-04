import pynvml

class NVMLInterface:
    def __init__(self):
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        self.device_name = pynvml.nvmlDeviceGetName(self.handle)

    def get_architecture_metrics(self):
        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            temp = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
            clocks = pynvml.nvmlDeviceGetClockInfo(self.handle, pynvml.NVML_CLOCK_GRAPHICS)
            
            # New: Power Management Unit (PMU) Telemetry
            power_draw = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0 # Watts
            power_limit = pynvml.nvmlDeviceGetEnforcedPowerLimit(self.handle) / 1000.0
            
            return {
                "gpc_utilization": util.gpu,
                "mc_utilization": util.memory,
                "vram_used_mb": mem.used // 1024**2,
                "core_clock_mhz": clocks,
                "temperature_c": temp,
                "power_draw_w": round(power_draw, 2),
                "power_limit_w": round(power_limit, 2)
            }
        except pynvml.NVMLError as e:
            return {"error": str(e)}

    def get_compute_processes(self):
        """Fetches the hardware scheduler's process allocation table"""
        try:
            procs = pynvml.nvmlDeviceGetComputeRunningProcesses(self.handle)
            process_list = []
            for p in procs:
                vram_used = p.usedGpuMemory // 1024**2 if p.usedGpuMemory else 0
                process_list.append((p.pid, vram_used))
            return process_list
        except pynvml.NVMLError:
            return []

    def shutdown(self):
        pynvml.nvmlShutdown()