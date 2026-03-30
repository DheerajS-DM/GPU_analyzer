import tkinter as tk
from tkinter import ttk

class AnalyzerDashboard:
    def __init__(self, root, hardware_interface, logger):
        self.root = root
        self.hw = hardware_interface
        self.logger = logger
        
        self.root.title(f"COA Hardware Analyzer - {self.hw.device_name}")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e1e")

        self._setup_ui()
        self.is_logging = False
        self._update_loop()

    def _setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2d2d2d", foreground="#00ff00", fieldbackground="#2d2d2d", font=('Consolas', 10))
        
        tk.Label(self.root, text="NVIDIA ARCHITECTURE & SCHEDULER TELEMETRY", bg="#1e1e1e", fg="#76b900", font=("Consolas", 14, "bold")).pack(pady=10)

        # Main Metrics Table
        self.tree = ttk.Treeview(self.root, columns=("Metric", "Value", "Unit"), show='headings', height=7)
        self.tree.heading("Metric", text="Hardware Sub-system")
        self.tree.heading("Value", text="Current State")
        self.tree.heading("Unit", text="Unit")
        self.tree.pack(padx=20, pady=5, fill='x')

        # Process Scheduler Table
        tk.Label(self.root, text="HARDWARE PROCESS ALLOCATION TABLE", bg="#1e1e1e", fg="#00a8ff", font=("Consolas", 12, "bold")).pack(pady=10)
        self.proc_tree = ttk.Treeview(self.root, columns=("PID", "VRAM"), show='headings', height=5)
        self.proc_tree.heading("PID", text="Process ID (PID)")
        self.proc_tree.heading("VRAM", text="Allocated VRAM (MB)")
        self.proc_tree.pack(padx=20, pady=5, fill='x')

        # Controls
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=10)
        self.log_btn = tk.Button(btn_frame, text="START CSV LOGGING", command=self.toggle_logging, bg="#444444", fg="white", font=("Consolas", 10))
        self.log_btn.pack()

    def toggle_logging(self):
        self.is_logging = not self.is_logging
        self.log_btn.config(text="STOP CSV LOGGING", bg="#76b900", fg="black") if self.is_logging else self.log_btn.config(text="START CSV LOGGING", bg="#444444", fg="white")

    def _update_loop(self):
        metrics = self.hw.get_architecture_metrics()
        processes = self.hw.get_compute_processes()
        
        if "error" not in metrics:
            data_rows = [
                ("Graphics Processing Cluster (GPC)", metrics["gpc_utilization"], "%"),
                ("Memory Controller (MC)", metrics["mc_utilization"], "%"),
                ("Execution Core Clock", metrics["core_clock_mhz"], "MHz"),
                ("T-Junction Temperature", metrics["temperature_c"], "°C"),
                ("Power Draw (PMU)", metrics["power_draw_w"], f"W / {metrics['power_limit_w']} W")
            ]

            # Update Main Metrics
            for i in self.tree.get_children(): self.tree.delete(i)
            for item in data_rows: self.tree.insert('', 'end', values=item)

            # Update Process Table
            for i in self.proc_tree.get_children(): self.proc_tree.delete(i)
            if not processes:
                self.proc_tree.insert('', 'end', values=("No Active Compute Processes", "0"))
            else:
                for pid, vram in processes:
                    self.proc_tree.insert('', 'end', values=(f"PID: {pid}", vram))

            if self.is_logging:
                self.logger.log_snapshot(metrics)

        self.root.after(1000, self._update_loop)