import tkinter as tk
from core_hardware import NVMLInterface
from telemetry_logger import HardwareLogger
from gui_dashboard import AnalyzerDashboard

def main():
    # Initialize Core Modules
    hw_interface = NVMLInterface()
    logger = HardwareLogger()

    # Initialize GUI
    root = tk.Tk()
    app = AnalyzerDashboard(root, hw_interface, logger)

    # Handle clean exit
    def on_closing():
        hw_interface.shutdown()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()