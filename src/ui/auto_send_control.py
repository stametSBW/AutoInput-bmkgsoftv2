import tkinter as tk
from tkinter import ttk
import threading
from ..auto_sender import AutoSender

class AutoSendControl(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.auto_sender = None
        self.auto_send_thread = None
        self.setup_ui()

    def setup_ui(self):
        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = ttk.Label(
            self.main_container,
            text="Auto Send Control",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Status frame
        status_frame = ttk.LabelFrame(self.main_container, text="Status")
        status_frame.pack(fill=tk.X, pady=(0, 20))

        self.status_label = ttk.Label(
            status_frame,
            text="Auto Send: Tidak Aktif",
            font=("Helvetica", 10)
        )
        self.status_label.pack(pady=10)

        # Control buttons
        button_frame = ttk.Frame(self.main_container)
        button_frame.pack(fill=tk.X)

        self.start_button = ttk.Button(
            button_frame,
            text="Start Auto Send",
            command=self.start_auto_send,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop Auto Send",
            command=self.stop_auto_send,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Headless mode checkbox
        self.headless_var = tk.BooleanVar(value=False)
        self.headless_checkbox = ttk.Checkbutton(
            self.main_container,
            text="Run in headless mode",
            variable=self.headless_var
        )
        self.headless_checkbox.pack(pady=10)

    def start_auto_send(self):
        if self.auto_sender is None:
            self.auto_sender = AutoSender(headless=self.headless_var.get())
            self.auto_send_thread = threading.Thread(target=self.auto_sender.start)
            self.auto_send_thread.daemon = True
            self.auto_send_thread.start()
            
            self.status_label.config(text="Auto Send: Aktif")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.headless_checkbox.config(state=tk.DISABLED)

    def stop_auto_send(self):
        if self.auto_sender is not None:
            self.auto_sender.stop()
            self.auto_sender = None
            self.auto_send_thread = None
            
            self.status_label.config(text="Auto Send: Tidak Aktif")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.headless_checkbox.config(state=tk.NORMAL) 