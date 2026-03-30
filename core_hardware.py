import pynvml

class NVMLInterface:
    def __init__(self):
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        self.device_name = pynvml.nvmlDeviceGetName(self.handle)

    def get_architecture_metrics(self):
        metrics = {
            "gpc_utilization": "N/A", "mc_utilization": "N/A", "vram_used_mb": "N/A",
            "core_clock_mhz": "N/A", "temperature_c": "N/A", 
            "power_draw_w": "N/A", "power_limit_w": "N/A",
            "throttle_status": "N/A" # Added to prevent a crash in telemetry_logger.py
        }
        
        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            metrics["gpc_utilization"] = util.gpu
            metrics["mc_utilization"] = util.memory
        except pynvml.NVMLError: pass
        
        try:
            mem = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            metrics["vram_used_mb"] = mem.used // 1024**2
        except pynvml.NVMLError: pass

        try:
            temp = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
            metrics["temperature_c"] = temp
        except pynvml.NVMLError: pass

        try:
            clocks = pynvml.nvmlDeviceGetClockInfo(self.handle, pynvml.NVML_CLOCK_GRAPHICS)
            metrics["core_clock_mhz"] = clocks
        except pynvml.NVMLError: pass

        try:
            power_draw = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0
            metrics["power_draw_w"] = round(power_draw, 2)
        except pynvml.NVMLError: pass

        try:
            power_limit = pynvml.nvmlDeviceGetEnforcedPowerLimit(self.handle) / 1000.0
            metrics["power_limit_w"] = round(power_limit, 2)
        except pynvml.NVMLError: pass

        return metrics

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